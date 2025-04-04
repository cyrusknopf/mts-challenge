import argparse
import json
import sys
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple, Union

import numpy as np
import pandas as pd
from polygon import ReferenceClient, StocksClient

warnings.filterwarnings("ignore")

# Scaling constants for calculating points
# see docs/scoring.md for more info
ROI_SCALE = 1.0
DIVERSITY_SCALE = 1.3
CLI_SAT_SCALE = 2.0
RAR_SCALE = 1.2

DEBUG = False


@dataclass
class Context:
    """Context struct"""

    timestamp: str
    start: str
    end: str
    age: int
    employed: bool
    salary: float
    budget: float
    dislikes: set


def mse_from_ideal(weights_map: list[int]):
    if len(weights_map) == 1:
        # One stock is NOT a portfolio, punish
        weights_map.append(10000000)

    weights = np.array(weights_map, dtype=float)
    n = weights.size

    if n == 0:
        return 0.0

    ideal = weights.sum() / n
    mse = np.mean((weights - ideal) ** 2)

    return mse


def get_tickers_agg_bars(
    client: StocksClient, data: List[Tuple[str, int]], start: str, end: str
) -> pd.DataFrame | None:
    df = pd.DataFrame(None, columns=["ticker", "v", "vw", "o", "c", "h", "l", "t", "n"])
    for ticker, qty in data:
        bars = client.get_aggregate_bars(
            ticker, from_date=start, to_date=end, timespan="day"
        )
        if "results" not in bars:
            return None
        tmpdf = pd.DataFrame(bars["results"])
        tmpdf["ticker"] = ticker
        tmpdf["qty"] = qty

        df = pd.concat([df, tmpdf])
    df.set_index(["t", "ticker"], inplace=True)
    df["value"] = df["c"] * df["qty"]
    return df


def init_price_breaches_threshold(df: pd.DataFrame, threshold: float) -> bool:
    return df.groupby(level=1).first()["value"].sum() > threshold


def is_industry_in_dislikes(
    stock: str,
    ticker_details: Dict[str, Dict],
    context: Context,
    sic_industry: Dict[str, List[str]],
) -> bool:
    stock_details = ticker_details[stock]
    sic_code = stock_details["results"]["sic_code"]
    for industry in sic_industry[sic_code]:
        if industry in context.dislikes:
            return True
    return False


def sharpe(
    df: pd.DataFrame,
    rates: pd.DataFrame,
    days: int = 252,
):

    # Group the values; this returns a Series
    values = df.groupby(level=0)["value"].apply(lambda x: x.sum())
    values.index = pd.to_datetime(values.index, unit="ms")

    # Convert the Series to a DataFrame
    values = values.to_frame(name="value")

    # Ensure both indexes are sorted
    values = values.sort_index()
    rates = rates.sort_index()

    nearest_idx = rates.index.get_indexer(values.index, method="nearest")

    values["returns"] = (values["value"] / values["value"].shift(1)) - 1
    daily_risk_free = ((1 + rates.iloc[nearest_idx]["value"] / 100) ** (1 / 252)) - 1
    values["risk_free_rate"] = daily_risk_free.values
    values["diff"] = values["returns"] - values["risk_free_rate"]

    value = values["diff"].mean() / values["diff"].std()
    value *= np.sqrt(days)
    return value


def sortino(
    df: pd.DataFrame,
    context: Context,
    rates: pd.DataFrame,
    days: int = 252,
):
    """
    Calculate the Sortino ratio which only considers downside volatility.
    """
    values = df.groupby(level=0)["value"].apply(lambda x: x.sum())
    values.index = pd.to_datetime(values.index, unit="ms")
    values = values.to_frame(name="value")
    values = values.sort_index()
    rates = rates.sort_index()
    nearest_idx = rates.index.get_indexer(values.index, method="nearest")

    values["returns"] = values["value"].pct_change()
    daily_risk_free = ((1 + rates.iloc[nearest_idx]["value"] / 100) ** (1 / 252)) - 1
    values["risk_free_rate"] = daily_risk_free.values
    values["excess_returns"] = values["returns"] - values["risk_free_rate"]

    # Only consider negative excess returns for downside risk
    downside_returns = values["excess_returns"].where(values["excess_returns"] < 0, 0)
    downside_deviation = downside_returns.std()

    mean_excess_return = values["excess_returns"].mean()
    # Avoid division by zero; if no downside volatility, default to Sharpe
    if downside_deviation == 0:
        return np.nan
    sortino_ratio = mean_excess_return / downside_deviation * np.sqrt(days)
    return sortino_ratio


def risk_profile(context: Context) -> float:
    """Risk profile returns a float from [0, 1.2] where a higher score indicates
    more a more risk_averse client"""

    def age_profile(age):
        x0 = 45  # inflection age
        k = 0.1  # steepness factor
        risk_tolerance_logistic = 1 / (1 + np.exp(k * (age - x0)))
        return risk_tolerance_logistic

    salary_budget_ratio = min(context.budget, context.salary) / max(1, context.salary)

    risk_factor = (age_profile(context.age) + salary_budget_ratio) / 2

    # FIXME: Think about employment_status harder.
    if not context.employed:
        risk_factor *= 1.2

    return risk_factor


def get_points(
    df: pd.DataFrame,
    profit: float,
    stocks: List[Tuple[str, int]],
    legal_stocks: list[tuple[str, int]],
    context: Context,
    unique_industries: Set[str],
    basedir: str,
    sic_industry: dict[str, list[str]],
    ticker_details: dict,
) -> int:
    n_allowed_industries = len(unique_industries) - len(context.dislikes)

    roi = return_on_investment(profit, context)
    diversity = diversity_score(
        df,
        stocks,
        unique_industries,
        n_allowed_industries,
        sic_industry,
        ticker_details,
    )
    client_sat = client_satisfaction(df, risk_profile(context))
    rar = risk_adjusted_returns(df, context, basedir)

    if DEBUG:
        print(f"{roi=}", f"{diversity=}", f"{client_sat=}", f"{rar=}")

    points = (
        ROI_SCALE * roi
        + DIVERSITY_SCALE * diversity
        + CLI_SAT_SCALE * client_sat
        + RAR_SCALE * rar
    )

    points = points * 10  # make a nicer scale for points

    # Dock fixed amount of points, if illegal
    if len(legal_stocks) != len(stocks):
        profit = 0.5 * profit if profit > 0 else profit * 1.5
        points = 0.5 * points if points > 0 else points * 1.5

    return points if profit > 0 else -abs(points)


def return_on_investment(profit: float, context: Context) -> float:
    """Return on investment is defined as the ratio of profit to initial budget"""
    return profit / context.budget


def diversity_score(
    df: pd.DataFrame,
    stocks: List[Tuple[str, int]],
    unique_industries: set[str],
    n_allowed_industries: int,
    sic_industry: dict[str, list[str]],
    ticker_details: dict,
) -> float:

    stock_quantity_prods = df.groupby(level=1).first()["value"]
    unique_stocks = set([s for s, _ in stocks])
    stock_counts = [stock_quantity_prods[s] for s in unique_stocks]
    stocks_per_industry = stock_count_per_industry(ticker_details, stocks, sic_industry)
    stock_mse = mse_from_ideal(stock_counts)
    sic_mse = mse_from_ideal(list(stocks_per_industry.values()))

    stock_score = np.log(1 + len(stocks)) / (1 + len(unique_stocks) * stock_mse)
    sic_score = (len(unique_industries) / n_allowed_industries) / (1 + sic_mse)

    return stock_score + sic_score


def stock_count_per_industry(
    ticker_details: dict,
    stocks: list[tuple[str, int]],
    sic_industry: dict[str, list[str]],
) -> dict[str, int]:
    """Returns how many stocks were invested per industry"""
    industry_count_map: dict[str, int] = {}

    # XXX: sic_industries map a code to a list of industries in a (theoretically)
    # many-many fashion. Visual inspection suggests that
    # len(sic_industries[TCKR]) is always one. This makes calculating
    # diversification harder. To workaround this, always assign stocks to the
    # **first industry** in the list.

    for tkr, quantity in stocks:
        sic_code = ticker_details[tkr]["results"]["sic_code"]
        industries = sic_industry[sic_code]

        if not industries:
            industry = "unmapped"
        else:
            industry = industries[0]

        if industry not in industry_count_map:
            industry_count_map[industry] = 0

        industry_count_map[industry] += quantity

    return industry_count_map


def client_satisfaction(df: pd.DataFrame, risk_profile: float) -> float:
    """Client satisfaction is a score between 0 and 1"""

    portfolio_risk = df["value"].std()  # using definition of portfolio volatility

    k = 2 - (risk_profile / 1.2)
    client_risk = df["value"].mean() * np.abs(1 - k)

    # "full marks" for not exceeding risk tolerance; otherwise score falls by
    # percentage overreached.
    if client_risk >= portfolio_risk:
        return 1

    return 1 - ((portfolio_risk - client_risk) / client_risk)


def risk_adjusted_returns(
    df: pd.DataFrame,
    context: Context,
    basedir: str,
) -> float:
    """Calculate the risk-adjusted returns using Sharpe and Sortino ratios"""
    rates = pd.read_csv(f"{basedir}/bond-rate.csv")
    rates.set_index("date", inplace=True)
    rates.index = pd.to_datetime(rates.index)

    rar = sharpe(df, rates)
    s_ratio = sortino(df, context, rates)
    if np.isnan(s_ratio):
        risk_adjusted = rar
    else:
        risk_adjusted = (rar + s_ratio) / 2

    return risk_adjusted


def evaluate(
    df: pd.DataFrame,
    stocks: List[Tuple[str, int]],
    context: Context,
    sic_industry: Dict[str, List[str]],
    unique_industries: Set[str],
    ref_client: ReferenceClient,
    basedir: str,
) -> Tuple[bool, str, float, int]:
    # Check did not send multiple stocks
    if len(stocks) != len(set([s for s, _ in stocks])):
        return False, f"Error: duplicate tickers: {stocks}", 0.0, -1

    if min([i for _, i in stocks]) <= 0:
        return False, f"Error: invalid stock weight: {stocks}", 0.0, -1

    if init_price_breaches_threshold(df, context.budget):
        # Breached the max price that someone has
        return False, "Error: budget breached", 0.0, -1

    # Verify all tickers exist and grab details
    ticker_details = {}
    for stock, _ in stocks:
        details = ref_client.get_ticker_details(stock)
        if details["status"] != "OK":
            return False, f"Error: invalid ticker: {stock}", 0.0, -1
        elif details["results"]["type"] != "CS":
            return (
                False,
                f"Error: invalid ticker type: {stock} of type {details['results']['type']}",
                0.0,
                -1,
            )
        ticker_details[stock] = details

    # Remove stocks if they are not legal, so we only calculate using the legal stocks.
    legal_stocks = [
        (stock, qty)
        for stock, qty in stocks
        if not is_industry_in_dislikes(stock, ticker_details, context, sic_industry)
    ]

    profit = (
        df.groupby(level=1).last()["value"].sum()
        - df.groupby(level=1).first()["value"].sum()
    )

    points = get_points(
        df,
        profit,
        stocks,
        legal_stocks,
        context,
        unique_industries,
        basedir,
        sic_industry,
        ticker_details,
    )

    return True, "", profit, points


def main(api_key: str, data: Dict[str, Union[List[Dict[str, int]], Any]]):
    stocks_client = StocksClient(api_key)
    ref_client = ReferenceClient(api_key)
    if "context" not in data:
        print("context not passed through")
        return

    with open(f"{args.basedir}/sic_industry.json", "r") as f:
        sic_industry = json.loads(f.read())
    with open(f"{args.basedir}/unique_industries.json", "r") as f:
        unique_industries = json.loads(f.read())

    context = Context(**data["context"])

    stocks = []
    for stock in data["stocks"]:
        stocks.append([stock["ticker"], stock["quantity"]])

    df = get_tickers_agg_bars(
        stocks_client,
        stocks,
        # TODO: replace string slicing with proper parsing
        #   https://stackoverflow.com/questions/1941927/convert-an-rfc-3339-time-to-a-standard-python-timestamp
        start=context.start.split("T")[0],
        end=context.end.split("T")[0],
    )
    if df is None:
        print(
            json.dumps(
                {
                    "passed": False,
                    "profit": 0.0,
                    "points": 0.0,  # Do not penalise this error
                    "error": f"invalid ticker(s) passed in {data['stocks']}",
                }
            )
        )
        return

    passed, error_message, profit, points = evaluate(
        df, stocks, context, sic_industry, unique_industries, ref_client, args.basedir
    )

    print(
        json.dumps(
            {
                "passed": passed,
                "profit": profit,
                "points": points,
                "error": error_message,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apikey", help="The polygon api key", required=True)
    parser.add_argument(
        "--basedir", help="Directory base to look for files.", default="./"
    )
    args = parser.parse_args()

    data = json.loads(sys.stdin.read())
    main(args.apikey, data)
