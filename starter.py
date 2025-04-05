import json
from time import sleep

import requests

URL = "mts-prism.com"
PORT = 8082

# Please do NOT share this information anywhere, unless you want your team to be cooked.
TEAM_API_CODE = "top 10 most glorious imperial rules"


def send_get_request(path):
    """
    Sends a HTTP GET request to the server.
    Returns:
        (success?, error or message)
    """
    headers = {"X-API-Code": TEAM_API_CODE}
    response = requests.get(f"http://{URL}:{PORT}/{path}", headers=headers)

    # Check whether there was an error sent from the server.
    # 200 is the HTTP Success status code, so we do not expect any
    # other response code.
    if response.status_code != 200:
        return (
            False,
            f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}",
        )
    return True, response.text


def send_post_request(path, data=None):
    """
    Sends a HTTP POST request to the server.
    Pass in the POST data to data, to send some message.
    Returns:
         (success?, error or message)
    """
    headers = {"X-API-Code": TEAM_API_CODE, "Content-Type": "application/json"}

    # Convert the data from python dictionary to JSON string,
    # which is the expected format to be passed
    data = json.dumps(data)
    response = requests.post(f"http://{URL}:{PORT}/{path}", data=data, headers=headers)

    # Check whether there was an error sent from the server.
    # 200 is the HTTP Success status code, so we do not expect any
    # other response code.
    if response.status_code != 200:
        return (
            False,
            f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}",
        )
    return True, response.text


def get_context():
    """
    Query the challenge server to request for a client to design a portfolio for.
    Returns:
        (success?, error or message)
    """
    return send_get_request("/request")


def get_my_current_information():
    """
    Query your team information.
    Returns:
        (success?, error or message)
    """
    return send_get_request("/info")


def send_portfolio(weighted_stocks):
    """
    Send portfolio stocks to the server for evaluation.
    Returns:
        (success?, error or message)
    """
    data = [
        {"ticker": weighted_stock[0], "quantity": weighted_stock[1]}
        for weighted_stock in weighted_stocks
    ]
    return send_post_request("/submit", data=data)


success, information = get_my_current_information()
if not success:
    print(f"Error: {information}")
print(f"Team information: ", information)

success, context = get_context()
if not success:
    print(f"Error: {context}")
print(f"Context provided: ", context)

sleep(8)
# Maybe do something with the context to generate this?
portfolio = [("AAPL", 1), ("MSFT", 1)]

success, response = send_portfolio(portfolio)
if not success:
    print(f"Error: {response}")
print(f"Evaluation response: ", response)
