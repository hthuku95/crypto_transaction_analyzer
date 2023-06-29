from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests

COIN_API_KEY = "ec455fb4-aab6-44bf-88af-279555e4aaa9"
CRYPTO_COMPARE_API_KEY = "42d127eac62b0177671afb0df449ed4cf7db75d5f9407af0e7d4724e86d1ee60"

erc20_address_one = "0xd9ba1Dbe38eB76307ec275F11CEd907033961bA1"
erc20_address_two = "0x4F196FdEdC51C7F0c9E33D1D9030d8EC5C5A238C"
erc20_address_three = "0x36928500bc1dcd7af6a2b4008875cc336b927d57"
ETHERSCAN_API_KEY = "K9XBVRXWXPGQGRT8JXV3DU8E2UPMYIUVP7"

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

def calculate_erc20_volumes(transactions):
    incoming_volume_usd = 0
    outgoing_volume_usd = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        value = int(tx['value']) / 10**18  # Convert value from wei to BUSD
        timestamp = int(tx['timeStamp'])
        address_from = tx['from']
        address_to = tx['to']

        if timestamp >= cutoff_date:
            usd_value = convert_to_usd(value, timestamp)
            print("USD value", usd_value)
            if usd_value is not None:
                if value < 0:  # Outgoing transaction
                    outgoing_volume_usd += usd_value
                    print("Outgoing transaction from:", address_from)
                elif value > 0:  # Incoming transaction
                    incoming_volume_usd += usd_value
                    print("Incoming transaction to:", address_to)

    return incoming_volume_usd, outgoing_volume_usd

def convert_eth_to_usd(value_eth, timestamp):
    # Fetch Ethereum to USD exchange rate from CoinCap API at the timestamp
    url = "https://api.coincap.io/v2/rates/ethereum/history"
    params = {
        'interval': 'm1',
        'start': timestamp,
        'end': timestamp + 60  # Add 60 seconds for 1-minute interval
    }
    headers = {
        'Accepts': 'application/json',
        'Authorization': f"Bearer {COIN_API_KEY}"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                price_usd = data['data'][0]['rateUsd']
                value_usd = value_eth * float(price_usd)
                return value_usd
            else:
                print("No price data available for Ethereum at the given timestamp")
                return None
        else:
            print(f"Error fetching Ethereum to USD exchange rate. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching Ethereum to USD exchange rate: {str(e)}")
        return None

erc20_one_transactions = fetch_erc20_transactions(erc20_address_one,ETHERSCAN_API_KEY)
erc20_two_transactions = fetch_erc20_transactions(erc20_address_two,ETHERSCAN_API_KEY)
erc20_three_transactions = fetch_erc20_transactions(erc20_address_three,ETHERSCAN_API_KEY)

print("erc20 one")
(a1,b1) = calculate_erc20_volumes(erc20_one_transactions)
print("Incoming1",a1)
print("Outgoing1",b1)
print("erc20 two")
(a2,b2) = calculate_erc20_volumes(erc20_two_transactions)
print("Incoming1",a2)
print("Outgoing1",b2)
print("erc20 three")
(a3,b3) = calculate_erc20_volumes(erc20_three_transactions)
print("Incoming1",a3)
print("Outgoing1",b3)