import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass
from pprint import pprint
from typing import Any, Dict, List, Set, Tuple, Union

import pandas as pd
from numpy.polynomial.legendre import legadd
from polygon import ReferenceClient, StocksClient


@dataclass
class Context:
    """Context struct"""

    start_date: str
    end_date: str
    age: int
    employment_status: bool
    salary: float
    budget: float
    dislikes: set


def get_tickers_agg_bars(
    client: StocksClient, data: List[Tuple[str, int]], start_date: str, end_date: str
) -> pd.DataFrame:
    df = pd.DataFrame(None, columns=["ticker", "v", "vw", "o", "c", "h", "l", "t", "n"])

    for ticker, qty in data:
        bars = client.get_aggregate_bars(
            ticker, from_date=start_date, to_date=end_date, timespan="day"
        )
        if "results" not in bars:
            raise Exception("empty data returned")
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


def evaluate(
    df: pd.DataFrame,
    stocks: List[Tuple[str, int]],
    context: Context,
    sic_industry: Dict[str, List[str]],
    unique_industries: Set[str],
    ref_client: ReferenceClient,
) -> Tuple[bool, str, float, float]:
    # Check did not send multiple stocks
    if len(stocks) != len(set([s for s, _ in stocks])):
        return False, f"Error: duplicate tickers: {stocks}", 0.0, -1.0

    if init_price_breaches_threshold(df, context.budget):
        # Breached the max price that someone has
        return False, "", 0.0, -1.0

    # Verify all tickers exist and grab details
    ticker_details = {}
    for stock, _ in stocks:
        details = ref_client.get_ticker_details(stock)
        if details["status"] != "OK":
            return False, f"Error: invalid ticker: {stock}", 0.0, -1.0
        ticker_details[stock] = details

    # Remove stocks if they are not legal, so we only calculate using the legal stocks.
    legal_stocks = [
        (stock, qty)
        for stock, qty in stocks
        if not is_industry_in_dislikes(stock, ticker_details, context, sic_industry)
    ]

    profit, points = 0.0, 0.0
    # FIXME: Forward test

    # Dock fixed amount of points, if illegal
    if len(legal_stocks) != len(stocks):
        profit *= 0.85
        points *= 0.85

    return True, "", profit, points


def main(api_key: str, data: Dict[str, Union[List[Tuple[str, int]] | Any]]):
    stocks_client = StocksClient(api_key)
    ref_client = ReferenceClient(api_key)
    if "context" not in data:
        print("context not passed through")
        return

    with open("sic_industry.json", "r") as f:
        sic_industry = json.loads(f.read())
    with open("unique_industries.json", "r") as f:
        unique_industries = json.loads(f.read())

    context = Context(**data["context"])

    df = get_tickers_agg_bars(
        stocks_client,
        data["stocks"],
        start_date=context.start_date,
        end_date=context.end_date,
    )

    passed, error_message, profit, points = evaluate(
        df, data["stocks"], context, sic_industry, unique_industries, ref_client
    )
    print(passed, profit, points, end="")
    if error_message:
        print(" |", error_message)
    else:
        print("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apikey", help="The polygon api key", required=True)
    args = parser.parse_args()

    data = json.loads(sys.stdin.read())
    main(args.apikey, data)
