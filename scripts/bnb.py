from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests
from dotenv import dotenv_values

env_vars = dotenv_values('.env')


CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

bnb_address = "0x3F10a43438cdF6B0E9Ef39dcA5F9438dd3326227"
BSCSCAN_API_KEY = env_vars.get('BSCSAN_API_KEY')

# Cache for storing fetched transactions
transaction_cache = {}

# Cache for storing USD conversion values
usd_cache = {}

def fetch_bnb_transactions(address, api_key):
    # Check if transactions are already cached
    if address in transaction_cache:
        return transaction_cache[address]
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
                # Cache the fetched transactions
                transaction_cache[address] = transactions
                return transactions
            else:
                print(f"BscScan API returned an error: {data['message']}")
        else:
            print(f"Error fetching BNB transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching BNB transactions for address {address}: {str(e)}")

    return []

def calculate_bnb_volumes(transactions, target_address):
    incoming_volume_usd = 0
    outgoing_volume_usd = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        value = int(tx['value']) / 10**18  # Convert value from wei to BUSD
        timestamp = int(tx['timeStamp'])
        address_from = tx['from']
        address_to = tx['to']
        print("value",value)
        print("timestamp",timestamp)
        print("cutoff date",cutoff_date)
        if timestamp >= cutoff_date:
            usd_value = convert_to_usd(value, timestamp)
            if usd_value is not None:
                if address_to.lower() == target_address.lower():  # Incoming transaction
                    incoming_volume_usd += usd_value
                    print("Incoming transaction to:", address_to)
                elif address_from.lower() == target_address.lower():  # Outgoing transaction
                    outgoing_volume_usd += usd_value
                    print("Outgoing transaction from:", address_from)

    return incoming_volume_usd, outgoing_volume_usd



def convert_to_usd(value, timestamp):
    # Check if conversion value is already cached
    if timestamp in usd_cache:
        return usd_cache[timestamp]
    api_url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=BNB&tsyms=USD&ts={timestamp}&api_key=CRYPTO_COMPARE_API_KEY"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        usd_price = data['BNB']['USD']
        usd_value = value * usd_price
        # Cache the USD conversion value
        usd_cache[timestamp] = usd_value
        return usd_value
    except requests.RequestException as e:
        print("Error occurred while converting to USD:", str(e))
        return None


bnb_transactions = fetch_bnb_transactions(bnb_address,BSCSCAN_API_KEY)
print(bnb_transactions)
(a,b) = calculate_bnb_volumes(bnb_transactions,bnb_address)
print("Incoming",a)
print("Outgoing",b)