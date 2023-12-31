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

# Ethereum address
ethereum_address = "0xdB3c617cDd2fBf0bb4309C325F47678e37F096D9"
ETHERSCAN_API_KEY = env_vars.get('ETHERSCAN_API_KEY')

# Cache for storing fetched transactions
transaction_cache = {}

# Cache for storing USD conversion values
usd_cache = {}

def fetch_ethereum_transactions(address, api_key):
    # Check if transactions are already cached
    if address in transaction_cache:
        return transaction_cache[address]
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
                # Cache the fetched transactions
                transaction_cache[address] = transactions
                return transactions
            else:
                print(f"Etherscan API returned an error: {data['message']}")
        else:
            print(f"Error fetching Ethereum transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching Ethereum transactions for address {address}: {str(e)}")

    return []

def calculate_eth_volumes(transactions, target_address):
    incoming_transactions = []
    outgoing_transactions = []

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        value = int(tx['value']) / 10**18  # Convert value from wei to ETH
        timestamp = int(tx['timeStamp'])
        address_from = tx['from']
        address_to = tx['to']

        if timestamp >= cutoff_date:
            usd_value = convert_to_usd(value, timestamp)
            if usd_value is not None:
                if address_to.lower() == target_address.lower():  # Incoming transaction
                    incoming_transactions.append({
                        'asset_type': 'Ethereum',
                        'transaction_hash': tx['hash'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_usd': usd_value
                    })
                elif address_from.lower() == target_address.lower():  # Outgoing transaction
                    outgoing_transactions.append({
                        'asset_type': 'Ethereum',
                        'transaction_hash': tx['hash'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_usd': usd_value
                    })

    return incoming_transactions, outgoing_transactions


def convert_to_usd(value, timestamp):
    # Check if conversion value is already cached
    if timestamp in usd_cache:
        return usd_cache[timestamp]
    api_url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=ETH&tsyms=USD&ts={timestamp}&api_key=CRYPTO_COMPARE_API_KEY"

    try:
        response = requests.get(api_url)
        data = response.json()
        usd_price = data['ETH']['USD']
        usd_value = value * usd_price
        # Cache the USD conversion value
        usd_cache[timestamp] = usd_value
        return usd_value
    except requests.RequestException as e:
        print("Error occurred while converting to USD:", str(e))
        return None

def export_transaction_data_to_csv(incoming_transactions, outgoing_transactions):
    filename = 'ethereum_transactions.csv'

    fieldnames = ['asset_type', 'transaction_hash', 'timestamp', 'value_usd']

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in incoming_transactions:
            writer.writerow(transaction)

        for transaction in outgoing_transactions:
            writer.writerow(transaction)

    generate_chart(incoming_transactions, outgoing_transactions, filename)

    print(f"Transaction data exported to {filename}")

def generate_chart(incoming_transactions, outgoing_transactions, filename):
    incoming_timestamps = [transaction['timestamp'] for transaction in incoming_transactions]
    incoming_values_usd = [transaction['value_usd'] for transaction in incoming_transactions]

    outgoing_timestamps = [transaction['timestamp'] for transaction in outgoing_transactions]
    outgoing_values_usd = [transaction['value_usd'] for transaction in outgoing_transactions]

    plt.figure(figsize=(12, 6))
    plt.plot(incoming_timestamps, incoming_values_usd, marker='o', linestyle='-', label='Incoming')
    plt.plot(outgoing_timestamps, outgoing_values_usd, marker='o', linestyle='-', label='Outgoing')
    plt.xlabel('Timestamp')
    plt.ylabel('USD Value')
    plt.title(f'Ethereum Transactions - {filename} - USD Value')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{filename.split(".")[0]}_usd_chart.png')
    plt.close()

ethereum_transactions = fetch_ethereum_transactions(ethereum_address, ETHERSCAN_API_KEY)
incoming_transactions, outgoing_transactions = calculate_eth_volumes(ethereum_transactions, ethereum_address)
export_transaction_data_to_csv(incoming_transactions, outgoing_transactions)