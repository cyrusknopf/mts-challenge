import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
from time import sleep, time
from typing import Any, Dict, List, Set, Tuple, Union

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import legadd
from polygon import ReferenceClient, StocksClient


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
    context: Context,
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
    def age_profile(age):
        x0 = 45  # inflection age
        k = 0.1  # steepness factor
        risk_tolerance_logistic = 1 / (1 + np.exp(k * (age - x0)))
        return risk_tolerance_logistic

    salary_budget_ratio = min(context.budget, context.salary) / max(1, context.salary)

    risk_factor = (age_profile(context.age) + salary_budget_ratio) / 2

    # FIXME: Think about employment_status harder.
    if context.employed:
        risk_factor *= 1.2

    return risk_factor


def get_points(
    df: pd.DataFrame,
    profit: float,
    stocks: List[Tuple[str, int]],
    context: Context,
    unique_industries: Set[str],
    basedir: str,
) -> float:

    # Load and prepare the rates DataFrame
    rates = pd.read_csv(f"{basedir}/bond-rate.csv")
    rates.set_index("date", inplace=True)
    rates.index = pd.to_datetime(rates.index)

    rar = sharpe(df, context, rates)
    s_ratio = sortino(df, context, rates)
    if np.isnan(s_ratio):
        risk_adjusted = rar
    else:
        risk_adjusted = (rar + s_ratio) / 2

    risk_factor = risk_profile(context)

    # Enhance diversity: consider both number of stocks and industry diversity.
    enhanced_diversity = np.log(1 + len(stocks)) + np.log(1 + len(unique_industries))

    points = abs(profit) * risk_adjusted / risk_factor * enhanced_diversity
    return points if profit > 0 else -abs(points)


def evaluate(
    df: pd.DataFrame,
    stocks: List[Tuple[str, int]],
    context: Context,
    sic_industry: Dict[str, List[str]],
    unique_industries: Set[str],
    ref_client: ReferenceClient,
    basedir: str,
) -> Tuple[bool, str, float, float]:
    # Check did not send multiple stocks
    if len(stocks) != len(set([s for s, _ in stocks])):
        return False, f"Error: duplicate tickers: {stocks}", 0.0, -1.0

    if min([i for _, i in stocks]) <= 0:
        return False, f"Error: invalid stock weight: {stocks}", 0.0, -1.0

    if init_price_breaches_threshold(df, context.budget):
        # Breached the max price that someone has
        return False, "Error: budget breached", 0.0, -1.0

    # Verify all tickers exist and grab details
    ticker_details = {}
    for stock, _ in stocks:
        details = ref_client.get_ticker_details(stock)
        if details["status"] != "OK":
            return False, f"Error: invalid ticker: {stock}", 0.0, -1.0
        elif details["results"]["type"] != "CS":
            return (
                False,
                f"Error: invalid ticker type: {stock} of type {details['results']['type']}",
                0.0,
                -1.0,
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

    points = get_points(df, profit, stocks, context, unique_industries, basedir)

    # Dock fixed amount of points, if illegal
    if len(legal_stocks) != len(stocks):
        profit *= 0.85
        points *= 0.85

    return True, "", profit, points


def main(api_key: str, data: Dict[str, Union[List[Dict[str, int]] | Any]]):
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
        # BAD
        start=context.start.split("T")[0],
        end=context.end.split("T")[0],
    )
    if df is None:
        print(
            json.dumps(
                {
                    "passed": False,
                    "profit": 0.0,
                    "points": -1.0,
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
