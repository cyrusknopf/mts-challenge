import argparse
import asyncio
import time

import aiohttp
import numpy as np
import requests
from tabulate import tabulate


def run_get(url: str, api_key: str) -> int:
    start: int = time.time_ns()
    headers = {"X-API-Code": api_key}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Request failed")
        return -1

    stop: int = time.time_ns()

    return stop - start


def serial_bm(args, request_url) -> np.ndarray:
    res_list = [run_get(request_url, args.apikey) for _ in range(args.iterations)]

    res = np.array(res_list) / 1e9

    return res


async def parallel_get(session, url):
    loop = asyncio.get_event_loop()
    start = loop.time()
    async with session.get(url) as response:
        await response.text()
        duration = loop.time() - start
        return duration


async def parallel_bm(args, request_url) -> (float, np.ndarray):
    headers = {"X-API-Code": args.apikey}
    start = time.time_ns()
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [parallel_get(session, request_url) for _ in range(args.iterations)]
        durations = await asyncio.gather(*tasks)
        res = np.array(durations)
    end = time.time_ns()
    return (end - start) / 1e9, res


def calculate_and_display_metrics(res: np.ndarray) -> None:
    metrics = [
        ["Mean", np.mean(res)],
        ["Standard Deviation", np.std(res)],
        ["Median", np.median(res)],
        ["Min", np.min(res)],
        ["Max", np.max(res)],
        ["25th Percentile", np.percentile(res, 25)],
        ["75th Percentile", np.percentile(res, 75)],
        ["Count", len(res)],
    ]

    print(tabulate(metrics, headers=["Metric", "Value"]))


async def main():
    parser = argparse.ArgumentParser(
        description="Benchmarking tool for PRISM server latency"
    )
    parser.add_argument(
        "-s",
        "--serial",
        type=bool,
        default=False,
        help="Whether to run the requests in parallel",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations to run the request(s) (default: 10).",
    )
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        required=True,
        help="Provide the API key to make the requests with",
    )
    parser.add_argument(
        "-H",
        "--hostname",
        type=str,
        default="mts-prism.com",
        help="Hostname for the request (default: localhost).",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8082,
        help="Port number for the request (default: 8082).",
    )

    args = parser.parse_args()

    # Build base URLs
    base_url = f"http://{args.hostname}:{args.port}"
    request_url = f"{base_url}/request"
    submit_url = f"{base_url}/submit"

    if args.serial:
        serial_res = serial_bm(args, request_url)
        calculate_and_display_metrics(serial_res)
    else:
        duration, _ = await parallel_bm(args, request_url)
        metrics = [
            ["Mean", (args.iterations) / duration],
            ["Count", args.iterations],
        ]
        print(tabulate(metrics, headers=["Metric", "Value"]))


if __name__ == "__main__":
    asyncio.run(main())
