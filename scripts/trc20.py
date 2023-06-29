from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests

COIN_API_KEY = "ec455fb4-aab6-44bf-88af-279555e4aaa9"
CRYPTO_COMPARE_API_KEY = "42d127eac62b0177671afb0df449ed4cf7db75d5f9407af0e7d4724e86d1ee60"

trc20_address = "TR9octGKwGi8EaBhphP8d8D6dTkSyMJKXW"
TRONSCAN_API_KEY = "60003d7a-10cd-4d0c-9abe-5a781c1971c2"

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

def calculate_trc20_volumes(transactions):
    incoming_volume_usd = 0
    outgoing_volume_usd = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        value_trx = float(tx['value']) / 10**6  # Convert value from sun to TRX
        timestamp = int(tx['timestamp'])

        if timestamp >= cutoff_date:
            usd_value = convert_trx_to_usd(value_trx, timestamp)
            if usd_value is not None:
                if trc20_address.lower() == tx['from'].lower():
                    outgoing_volume_usd += usd_value
                if trc20_address.lower() == tx['to'].lower():
                    incoming_volume_usd += usd_value

    return incoming_volume_usd, outgoing_volume_usd

def convert_trx_to_usd(value_trx, timestamp):
    # Fetch TRX to USD exchange rate from CoinCap API at the timestamp
    url = "https://api.coincap.io/v2/rates/tron/history"
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
                value_usd = value_trx * float(price_usd)
                return value_usd
            else:
                print("No price data available for TRON at the given timestamp")
                return None
        else:
            print(f"Error fetching TRX to USD exchange rate. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching TRX to USD exchange rate: {str(e)}")
        return None
        

trc20_transactions  = fetch_trc20_transactions(trc20_address,TRONSCAN_API_KEY)
(a,b) = calculate_trc20_volumes(trc20_transactions)
print("Incoming",a)
print("Outgoing",b)
