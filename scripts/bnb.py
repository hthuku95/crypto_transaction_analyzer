from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests

COIN_API_KEY = "ec455fb4-aab6-44bf-88af-279555e4aaa9"
CRYPTO_COMPARE_API_KEY = "42d127eac62b0177671afb0df449ed4cf7db75d5f9407af0e7d4724e86d1ee60"

bnb_address = "0x3F10a43438cdF6B0E9Ef39dcA5F9438dd3326227"
BSCSCAN_API_KEY = "Y5VBBSWUKS4VIZ6S1HCKVCW27XK7VU8X9J"

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


def calculate_bnb_volumes(transactions):
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

import requests

def convert_to_usd(value, timestamp):
    api_url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=BNB&tsyms=USD&ts={timestamp}&api_key=CRYPTO_COMPARE_API_KEY"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        usd_price = data['BNB']['USD']
        usd_value = value * usd_price
        return usd_value
    except requests.RequestException as e:
        print("Error occurred while converting to USD:", str(e))
        return None


bnb_transactions = fetch_bnb_transactions(bnb_address,BSCSCAN_API_KEY)

(a,b) = calculate_bnb_volumes(bnb_transactions)
print("Incoming",a)
print("Outgoing",b)