from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime, timedelta
import json
from web3 import Web3
import requests
from dotenv import dotenv_values
import csv

env_vars = dotenv_values('.env')

CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

erc20_address_one = "0xd9ba1Dbe38eB76307ec275F11CEd907033961bA1"
erc20_address_two = "0x4F196FdEdC51C7F0c9E33D1D9030d8EC5C5A238C"
erc20_address_three = "0x36928500bc1dcd7af6a2b4008875cc336b927d57"
ETHERSCAN_API_KEY = env_vars.get('ETHERSCAN_API_KEY')

# Cache for storing fetched transactions
transaction_cache = {}

# Cache for storing USD conversion values
usd_cache = {}

def fetch_erc20_transactions(address, api_key):
    # Check if transactions are already cached
    if address in transaction_cache:
        return transaction_cache[address]
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
                # Cache the fetched transactions
                transaction_cache[address] = transactions
                return transactions
            else:
                print(f"Etherscan API returned an error: {data['message']}")
        else:
            print(f"Error fetching ERC20 transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching ERC20 transactions for address {address}: {str(e)}")

    return []

def calculate_erc20_volumes(transactions, target_address):
    incoming_transactions = []
    outgoing_transactions = []

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        value_wei = int(tx['value'])
        value_eth = value_wei / 10**18  # Convert value from wei to ETH
        timestamp = int(tx['timeStamp'])
        address_from = tx['from']
        address_to = tx['to']

        if timestamp >= cutoff_date:
            usd_value = convert_to_usd(value_eth, timestamp)
            if usd_value is not None:
                if address_to.lower() == target_address.lower():  # Incoming transaction
                    incoming_transactions.append({
                        'asset_type': 'ERC20',
                        'transaction_hash': tx['hash'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_eth': value_eth,
                        'value_usd': usd_value
                    })
                elif address_from.lower() == target_address.lower():  # Outgoing transaction
                    outgoing_transactions.append({
                        'asset_type': 'ERC20',
                        'transaction_hash': tx['hash'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_eth': value_eth,
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


def export_transaction_data_to_csv(transactions, filename):
    fieldnames = ['asset_type', 'transaction_hash', 'timestamp', 'value_eth', 'value_usd']

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in transactions:
            writer.writerow(transaction)

    print(f"Transaction data exported to {filename}")

erc20_one_transactions = fetch_erc20_transactions(erc20_address_one, ETHERSCAN_API_KEY)
erc20_two_transactions = fetch_erc20_transactions(erc20_address_two, ETHERSCAN_API_KEY)
erc20_three_transactions = fetch_erc20_transactions(erc20_address_three, ETHERSCAN_API_KEY)

incoming1, outgoing1 = calculate_erc20_volumes(erc20_one_transactions, erc20_address_one)
incoming2, outgoing2 = calculate_erc20_volumes(erc20_two_transactions, erc20_address_two)
incoming3, outgoing3 = calculate_erc20_volumes(erc20_three_transactions, erc20_address_three)

export_transaction_data_to_csv(incoming1, 'erc20_one_incoming.csv')
export_transaction_data_to_csv(outgoing1, 'erc20_one_outgoing.csv')
export_transaction_data_to_csv(incoming2, 'erc20_two_incoming.csv')
export_transaction_data_to_csv(outgoing2, 'erc20_two_outgoing.csv')
export_transaction_data_to_csv(incoming3, 'erc20_three_incoming.csv')
export_transaction_data_to_csv(outgoing3, 'erc20_three_outgoing.csv')