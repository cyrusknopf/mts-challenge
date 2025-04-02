#!/usr/bin/env python3
import argparse
import json
import threading
import time

import requests


def parse_orders(orders_list):
    """
    Converts a list of orders in the form TICKER:QUANTITY to a list of dictionaries.
    """
    orders = []
    for order in orders_list:
        try:
            ticker, quantity = order.split(":")
            orders.append({"ticker": ticker, "quantity": int(quantity)})
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid order format: {order}. Please use TICKER:QUANTITY (e.g. AAPL:1)."
            )
    return orders


def send_iteration(iteration, args, orders, request_url, submit_url):
    # Rotate over X-API-Codes if more than one provided
    code = args.x_api_codes[iteration % len(args.x_api_codes)]
    headers = {"X-API-Code": code}
    print(f"\nIteration {iteration+1} using X-API-Code: {code}")

    # Define GET and POST request functions
    def send_get():
        get_response = requests.get(request_url, headers=headers)
        if get_response.status_code != 200:
            print(
                f"Error during GET request: {get_response.status_code} | {get_response.text}"
            )
        else:
            print("GET Response:")
            print(json.dumps(get_response.json(), indent=2))

    def send_post():
        post_response = requests.post(submit_url, headers=headers, json=orders)
        if post_response.status_code != 200:
            print(
                f"Error during POST request: {post_response.status_code} | {post_response.text}"
            )
        else:
            print("POST Response:")
            print(json.dumps(post_response.json(), indent=2))

    # Create threads for GET and POST concurrently
    get_thread = threading.Thread(target=send_get)
    post_thread = threading.Thread(target=send_post)

    get_thread.start()
    post_thread.start()

    # Wait for both requests to complete
    get_thread.join()
    post_thread.join()


def main():
    parser = argparse.ArgumentParser(
        description="Multithreaded script to send GET and POST requests with X-API-Code header."
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations to run the requests (default: 1).",
    )
    parser.add_argument(
        "-c",
        "--x-api-codes",
        nargs="+",
        required=True,
        help=(
            "List of X-API-Codes. If more than one is provided, they will be rotated over iterations. "
            "Example: --x-api-codes code1 code2 code3"
        ),
    )
    parser.add_argument(
        "-o",
        "--orders",
        nargs="+",
        required=True,
        help=(
            "List of orders in the format TICKER:QUANTITY. "
            "Example: --orders AAPL:1 MSFT:20"
        ),
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
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=0,
        help="Optional delay in seconds between starting each iteration (default: 0).",
    )

    args = parser.parse_args()

    # Parse the orders argument
    try:
        orders = parse_orders(args.orders)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # Build base URLs
    base_url = f"http://{args.hostname}:{args.port}"
    request_url = f"{base_url}/request"
    submit_url = f"{base_url}/submit"

    # Create a list to hold iteration threads
    iteration_threads = []

    # Start each iteration in its own thread
    for i in range(args.iterations):
        thread = threading.Thread(
            target=send_iteration, args=(i, args, orders, request_url, submit_url)
        )
        thread.start()
        iteration_threads.append(thread)
        # Optional delay between starting each iteration
        if args.delay > 0:
            time.sleep(args.delay)

    # Wait for all iterations to complete
    for thread in iteration_threads:
        thread.join()


if __name__ == "__main__":
    main()
