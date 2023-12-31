from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests
from dotenv import dotenv_values
import csv
import matplotlib.pyplot as plt


env_vars = dotenv_values('.env')

CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

btc_address_one = "Bc1qzh8rga4vvvzzdan5jqhz5ljygt0hvdp7j74qzn1GrwDkr33gT6"
btc_address_two = "1GrwDkr33gT6LuumniYjKEGjTLhsL5kmqC"
BITCOIN_EXPLORER_API_KEY = env_vars.get('BITCOIN_EXPLORER_API_KEY')

# Cache for storing fetched transactions
transaction_cache = {}

# Cache for storing USD conversion values
usd_cache = {}

def fetch_bitcoin_transactions(address, api_key):
    # Check if transactions are already cached
    if address in transaction_cache:
        return transaction_cache[address]
    # Blockcypher API configuration
    blockcypher_api_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
    headers = {'Content-Type': 'application/json'}

    try:
        params = {'token': api_key}  # API key may be required for authentication
        response = requests.get(blockcypher_api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('txs', [])
            # Cache the fetched transactions
            transaction_cache[address] = transactions
            return transactions
        else:
            print(f"Error fetching Bitcoin transactions for address {address}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Exception occurred while fetching Bitcoin transactions for address {address}: {str(e)}")

    return []

def calculate_bitcoin_volumes(transactions):
    incoming_transactions = []
    outgoing_transactions = []

    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        outputs = tx.get('outputs', [])
        inputs = tx.get('inputs', [])

        output_value = sum([int(output.get('value', 0)) / 10**8 for output in outputs])
        input_value = sum([int(input.get('output_value', 0)) / 10**8 for input in inputs])

        timestamp_str = tx.get('received', '')

        try:
            timestamp_formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%S.%f'
            ]

            for timestamp_format in timestamp_formats:
                try:
                    timestamp_dt = datetime.strptime(timestamp_str, timestamp_format)
                    timestamp = timestamp_dt.timestamp()

                    if timestamp >= cutoff_date:
                        if output_value > 0:
                            usd_value = convert_to_usd(output_value, timestamp)
                            if usd_value is not None:
                                outgoing_transactions.append({
                                    'asset_type': 'Bitcoin',
                                    'transaction_hash': tx.get('hash'),
                                    'timestamp': timestamp_dt.strftime('%d/%m/%Y'),
                                    'value_usd': usd_value
                                })
                        elif input_value > 0:
                            usd_value = convert_to_usd(input_value, timestamp)
                            if usd_value is not None:
                                incoming_transactions.append({
                                    'asset_type': 'Bitcoin',
                                    'transaction_hash': tx.get('hash'),
                                    'timestamp': timestamp_dt.strftime('%d/%m/%Y'),
                                    'value_usd': usd_value
                                })
                        break

                except ValueError:
                    continue

            else:
                print(f"Invalid timestamp format for transaction: {tx}")

        except ValueError:
            print(f"Invalid timestamp format for transaction: {tx}")

    return incoming_transactions, outgoing_transactions

def export_transaction_data_to_csv(incoming_transactions, outgoing_transactions,address):
    filename = f'bitcoin_transactions-{address}.csv'

    fieldnames = ['asset_type', 'transaction_hash', 'timestamp', 'value_usd']

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in incoming_transactions:
            writer.writerow(transaction)

        for transaction in outgoing_transactions:
            writer.writerow(transaction)

         # Generate charts
        generate_charts(incoming_transactions, outgoing_transactions,address)

    print(f"Transaction data exported to {filename}")

# Generating Charts

def generate_charts(incoming_transactions, outgoing_transactions,address):
    # Extract timestamps and corresponding USD values
    incoming_timestamps = [transaction['timestamp'] for transaction in incoming_transactions]
    incoming_values = [transaction['value_usd'] for transaction in incoming_transactions]

    outgoing_timestamps = [transaction['timestamp'] for transaction in outgoing_transactions]
    outgoing_values = [transaction['value_usd'] for transaction in outgoing_transactions]

    # Generate incoming transactions chart
    plt.figure(figsize=(12, 6))
    plt.plot(incoming_timestamps, incoming_values, marker='o', linestyle='-', label='Incoming Transactions')
    plt.xlabel('Timestamp')
    plt.ylabel('USD Value')
    plt.title('Bitcoin Incoming Transactions')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'incoming_transactions_chart_{address}.png')
    plt.close()

    # Generate outgoing transactions chart
    plt.figure(figsize=(12, 6))
    plt.plot(outgoing_timestamps, outgoing_values, marker='o', linestyle='-', label='Outgoing Transactions')
    plt.xlabel('Timestamp')
    plt.ylabel('USD Value')
    plt.title('Bitcoin Outgoing Transactions')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outgoing_transactions_chart.png')
    plt.close()

    print("Charts generated.")

# Converting to USD
def convert_to_usd(amount, timestamp):
    # Check if conversion value is already cached
    if timestamp in usd_cache:
        return usd_cache[timestamp]
    url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=USD&ts={timestamp}&api_key={CRYPTO_COMPARE_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            price_data = data.get('BTC', {})
            usd_price = price_data.get('USD')
            
            if usd_price is not None:
                usd_value = amount * usd_price
                # Cache the USD conversion value
                usd_cache[timestamp] = usd_value
                return usd_value
        
        print(f"Error occurred while converting to USD: {data.get('Message', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    
    return None

# Example usage:
bitcoin_one_transactions = fetch_bitcoin_transactions(btc_address_one, BITCOIN_EXPLORER_API_KEY)
bitcoin_two_transactions = fetch_bitcoin_transactions(btc_address_two, BITCOIN_EXPLORER_API_KEY)
incoming_transactions, outgoing_transactions = calculate_bitcoin_volumes(bitcoin_one_transactions)
incoming_transactions2, outgoing_transactions2 = calculate_bitcoin_volumes(bitcoin_two_transactions)
export_transaction_data_to_csv(incoming_transactions, outgoing_transactions,btc_address_one)
export_transaction_data_to_csv(incoming_transactions2, outgoing_transactions2,btc_address_two)

