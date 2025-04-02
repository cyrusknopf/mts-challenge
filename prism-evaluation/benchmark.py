import argparse
import requests
import time
import numpy as np
from tabulate import tabulate

def run_get(url : str, api_key : str) -> int:
    start : int = time.time_ns()
    headers = { "X-API-Code" : api_key }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Request failed")
        return -1

    stop : int = time.time_ns()

    return stop - start

def main():
    parser = argparse.ArgumentParser(
        description="Benchmarking tool for PRISM server latency"
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
        help="Provide the API key to make the requests with"
    )
    parser.add_argument(
        "-H",
        "--hostname",
        type=str,
        default="localhost",
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

    res_list = [run_get(request_url, args.apikey) for _ in range(args.iterations)]
    res = np.array(res_list) / 1e9


    metrics = [
        ["Mean", np.mean(res)],
        ["Standard Deviation", np.std(res)],
        ["Median", np.median(res)],
        ["Min", np.min(res)],
        ["Max", np.max(res)],
        ["25th Percentile", np.percentile(res, 25)],
        ["75th Percentile", np.percentile(res, 75)],
        ["Count", len(res)]
    ]

    print(tabulate(metrics, headers=["Metric", "Value"]))

if __name__ == "__main__":
    main()
