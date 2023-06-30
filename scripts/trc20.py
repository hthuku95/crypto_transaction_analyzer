from datetime import datetime, timedelta
import requests
from dotenv import dotenv_values
import csv
import matplotlib.pyplot as plt
env_vars = dotenv_values('.env')
from dotenv import dotenv_values

env_vars = dotenv_values('.env')

trc20_address = "TR9octGKwGi8EaBhphP8d8D6dTkSyMJKXW"
TRONSCAN_API_KEY = env_vars.get('TRONSCAN_API_KEY')
CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

# Cache for storing fetched transactions
transaction_cache = {}

# Cache for storing USD conversion values
usd_cache = {}

def fetch_trc20_transactions(address, api_key):
    # Check if transactions are already cached
    if address in transaction_cache:
        return transaction_cache[address]
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
            # Cache the fetched transactions
            transaction_cache[address] = transactions
            return transactions
        else:
            print(f"Error fetching TRC20 transactions for address {address}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while fetching TRC20 transactions for address {address}: {str(e)}")

    return []

def calculate_trc20_volumes(transactions):
    incoming_transactions = []
    outgoing_transactions = []

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    for tx in transactions:
        contract_data = tx.get('raw_data', {}).get('contract', [{}])[0].get('parameter', {}).get('value', {})
        if 'amount' not in contract_data:
            continue

        value_trx = float(contract_data['amount']) / 10**6  # Convert value from sun to TRX
        timestamp = int(tx['block_timestamp']) / 1000  # Convert timestamp to seconds

        if timestamp >= cutoff_date:
            usd_value = convert_trx_to_usd(value_trx, timestamp)
            if usd_value is not None:
                if value_trx < 0:  # Outgoing transaction
                    outgoing_transactions.append({
                        'asset_type': 'TRC20',
                        'transaction_hash': tx['txID'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_trx': abs(value_trx),
                        'value_usd': abs(usd_value)
                    })
                elif value_trx > 0:  # Incoming transaction
                    incoming_transactions.append({
                        'asset_type': 'TRC20',
                        'transaction_hash': tx['txID'],
                        'timestamp': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y'),
                        'value_trx': value_trx,
                        'value_usd': usd_value
                    })

    return incoming_transactions, outgoing_transactions

def convert_trx_to_usd(value_trx, timestamp):
    # Check if conversion value is already cached
    if timestamp in usd_cache:
        return usd_cache[timestamp]
    api_url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=TRX&tsyms=USD&ts={timestamp}&api_key={CRYPTO_COMPARE_API_KEY}"

    try:
        response = requests.get(api_url)
        data = response.json()
        usd_price = data['TRX']['USD']
        usd_value = value_trx * usd_price
        # Cache the USD conversion value
        usd_cache[timestamp] = usd_value
        return usd_value
    except requests.RequestException as e:
        print("Error occurred while converting TRX to USD:", str(e))
        return None

def export_transaction_data_to_csv(transactions, filename):
    fieldnames = ['asset_type', 'transaction_hash', 'timestamp', 'value_trx', 'value_usd']

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in transactions:
            writer.writerow(transaction)
    
    generate_chart(transactions, filename)

    print(f"Transaction data exported to {filename}")

def generate_chart(transactions, filename):
    timestamps = [transaction['timestamp'] for transaction in transactions]
    values_usd = [transaction['value_usd'] for transaction in transactions]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values_usd, marker='o', linestyle='-', label='TRC20')
    plt.xlabel('Timestamp')
    plt.ylabel('USD Value')
    plt.title(f'TRC20 Transactions - {filename} - USD Value')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{filename.split(".")[0]}_usd_chart.png')
    plt.close()

trc20_transactions = fetch_trc20_transactions(trc20_address, TRONSCAN_API_KEY)
incoming_transactions, outgoing_transactions = calculate_trc20_volumes(trc20_transactions)

export_transaction_data_to_csv(incoming_transactions, 'incoming_trx_transactions.csv')
export_transaction_data_to_csv(outgoing_transactions, 'outgoing_trx_transactions.csv')
