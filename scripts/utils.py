from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests

COIN_MARKET_CAP_API_KEY = "5662e1f7-7758-49c3-82a7-9569fb9ea99c"

# Fetching the transactions
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

def fetch_erc20_transactions(address, api_key):
    # Ethereum configuration
    etherscan_api_url = 'https://api.etherscan.io/api'

    # Parameters for API request
    params = {
        'module': 'account',
        'action': 'tokentx',
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
            print(f"Error fetching ERC20 transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching ERC20 transactions for address {address}: {str(e)}")

    return []


def fetch_bitcoin_transactions(address,api_key):
    pass

def fetch_busd_transactions(address, api_key):
    # BscScan API configuration
    bscscan_api_url = 'https://api.bscscan.com/api'

    # Parameters for API request
    params = {
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': '0xe9e7cea3dedca5984780bafc599bd69add087d56',  # Correct BUSD contract address
        'address': address,
        'apikey': api_key,
    }

    try:
        response = requests.get(bscscan_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1':
                transactions = data['result']
                return transactions
            else:
                print(f"BscScan API returned an error: {data['message']}")
        else:
            print(f"Error fetching BUSD transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching BUSD transactions for address {address}: {str(e)}")

    return []

def fetch_bnb_transactions(address, api_key):
    # BscScan API configuration
    bscscan_api_url = 'https://api.bscscan.com/api'

    # Parameters for API request
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'apikey': api_key,
    }

    try:
        response = requests.get(bscscan_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1':
                transactions = data['result']
                return transactions
            else:
                print(f"BscScan API returned an error: {data['message']}")
        else:
            print(f"Error fetching BNB transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching BNB transactions for address {address}: {str(e)}")

    return []

def fetch_trc20_transactions(address, api_key):
    # TronGrid API configuration
    trongrid_api_url = 'https://api.trongrid.io/v1/accounts/{address}/transactions'
    headers = {
        'TRON-PRO-API-KEY': api_key,
    }

    try:
        url = trongrid_api_url.format(address=address)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            return transactions
        else:
            print(f"Error fetching TRC20 transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching TRC20 transactions for address {address}: {str(e)}")

    return []


# Calculating Volumes
def calculate_eth_volumes(transactions):
    incoming_volume = 0
    outgoing_volume = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    print(transactions)
    for tx in transactions:
        value = float(tx['value']) / 10 ** 18  # Convert value from wei to ether
        timestamp = int(tx['timeStamp'])

        if timestamp >= cutoff_date:
            if tx['from'] == ethereum_address:
                outgoing_volume += value
            if tx['to'] == ethereum_address:
                incoming_volume += value

    return incoming_volume, outgoing_volume

def calculate_erc20_volumes(transactions):
    pass

def calculate_bitcoin_volumes(transactions):
    pass

def calculate_busd_volumes(transactions):
    pass

def calculate_bnb_volumes(transactions):
    pass

def calculate_trc20_volumes(transactions):
    pass


