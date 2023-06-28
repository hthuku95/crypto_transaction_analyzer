from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests

COIN_MARKET_CAP_API_KEY = "5662e1f7-7758-49c3-82a7-9569fb9ea99c"
ETHERSCAN_API_KEY = "K9XBVRXWXPGQGRT8JXV3DU8E2UPMYIUVP7"

def fetch_transaction_data():
    pass

def fetch_coin_market_cap_data():
    url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start':'1',
        'limit':'5000',
        'convert':'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COIN_MARKET_CAP_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def fetch_ethereum_transactions(address, api_key):
    # Ethereum configuration
    etherscan_api_url = 'https://api.etherscan.io/api'

    # Parameters for API request
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'apikey': api_key,
    }

    try:
        response = requests.get(etherscan_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1':
                transactions = data['result']
                return transactions
            else:
                print(f"Etherscan API returned an error: {data['message']}")
        else:
            print(f"Error fetching Ethereum transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching Ethereum transactions for address {address}: {str(e)}")

    return []

