from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests
from dotenv import dotenv_values

env_vars = dotenv_values('.env')

CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

btc_address_one = "Bc1qzh8rga4vvvzzdan5jqhz5ljygt0hvdp7j74qzn1GrwDkr33gT6"
btc_address_two = "1GrwDkr33gT6LuumniYjKEGjTLhsL5kmqC"
BITCOIN_EXPLORER_API_KEY = env_vars.get('BITCOIN_EXPLORER_API_KEY')

def fetch_bitcoin_transactions(address, api_key):
    # Blockcypher API configuration
    blockcypher_api_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
    headers = {'Content-Type': 'application/json'}

    try:
        params = {'token': api_key}  # API key may be required for authentication
        response = requests.get(blockcypher_api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('txs', [])
            return transactions
        else:
            print(f"Error fetching Bitcoin transactions for address {address}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Exception occurred while fetching Bitcoin transactions for address {address}: {str(e)}")

    return []

def calculate_bitcoin_volumes(transactions):
    incoming_volume_usd = 0
    outgoing_volume_usd = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        outputs = tx.get('outputs', [])
        inputs = tx.get('inputs', [])

        # Calculate the total output value for the current transaction (outgoing transactions)
        output_value = sum([int(output.get('value', 0)) / 10**8 for output in outputs])

        # Calculate the total input value for the current transaction (incoming transactions)
        input_value = sum([int(input.get('output_value', 0)) / 10**8 for input in inputs])

        timestamp_str = tx.get('received', '')  # Get the 'received' timestamp as a string

        try:
            timestamp_formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',  # Format with milliseconds and 'Z' at the end
                '%Y-%m-%dT%H:%M:%S.%f'  # Format with milliseconds
            ]

            for timestamp_format in timestamp_formats:
                try:
                    timestamp_dt = datetime.strptime(timestamp_str, timestamp_format)
                    timestamp = timestamp_dt.timestamp()

                    if timestamp >= cutoff_date:
                        if output_value > 0:  # Outgoing transaction
                            usd_value = convert_to_usd(output_value, timestamp)
                            print("USD Value",usd_value)
                            if usd_value is not None:
                                outgoing_volume_usd += usd_value
                        elif input_value > 0:  # Incoming transaction
                            usd_value = convert_to_usd(input_value, timestamp)
                            print("USD Value",usd_value)
                            if usd_value is not None:
                                incoming_volume_usd += usd_value
                        break

                except ValueError:
                    continue

            else:
                print(f"Invalid timestamp format for transaction: {tx}")

        except ValueError:
            print(f"Invalid timestamp format for transaction: {tx}")

    return incoming_volume_usd, outgoing_volume_usd

def convert_to_usd(amount, timestamp):
    url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=USD&ts={timestamp}&api_key={CRYPTO_COMPARE_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            price_data = data.get('BTC', {})
            usd_price = price_data.get('USD')
            
            if usd_price is not None:
                usd_value = amount * usd_price
                return usd_value
        
        print(f"Error occurred while converting to USD: {data.get('Message', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    
    return None

bitcoin_one_transactions = fetch_bitcoin_transactions(btc_address_one,BITCOIN_EXPLORER_API_KEY)
bitcoin_two_transactions = fetch_bitcoin_transactions(btc_address_two,BITCOIN_EXPLORER_API_KEY)
calculate_bitcoin_volumes(bitcoin_one_transactions)
calculate_bitcoin_volumes(bitcoin_two_transactions)

