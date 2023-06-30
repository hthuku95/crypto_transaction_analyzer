from datetime import datetime, timedelta
import requests
from dotenv import dotenv_values

env_vars = dotenv_values('.env')
from dotenv import dotenv_values

env_vars = dotenv_values('.env')

trc20_address = "TR9octGKwGi8EaBhphP8d8D6dTkSyMJKXW"
TRONSCAN_API_KEY = env_vars.get('TRONSCAN_API_KEY')
CRYPTO_COMPARE_API_KEY = env_vars.get('CRYPTO_COMPARE_API_KEY')

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
        contract_data = tx.get('raw_data', {}).get('contract', [{}])[0].get('parameter', {}).get('value', {})
        if 'amount' not in contract_data:
            continue

        value_trx = float(contract_data['amount']) / 10**6  # Convert value from sun to TRX
        timestamp = int(tx['block_timestamp']) / 1000  # Convert timestamp to seconds

        if timestamp >= cutoff_date:
            usd_value = convert_trx_to_usd(value_trx, timestamp)
            if usd_value is not None:
                if value_trx < 0:  # Outgoing transaction
                    outgoing_volume_usd += usd_value
                    print("Outgoing transaction from:", contract_data['owner_address'])
                elif value_trx > 0:  # Incoming transaction
                    incoming_volume_usd += usd_value
                    print("Incoming transaction to:", contract_data['to_address'])

    return incoming_volume_usd, outgoing_volume_usd

def convert_trx_to_usd(value_trx, timestamp):
    api_url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym=TRX&tsyms=USD&ts={timestamp}&api_key={CRYPTO_COMPARE_API_KEY}"

    try:
        response = requests.get(api_url)
        data = response.json()
        usd_price = data['TRX']['USD']
        usd_value = value_trx * usd_price
        return usd_value
    except requests.RequestException as e:
        print("Error occurred while converting TRX to USD:", str(e))
        return None

trc20_transactions = fetch_trc20_transactions(trc20_address, TRONSCAN_API_KEY)
print(trc20_transactions[-1])
print(trc20_transactions[-2])
print(trc20_transactions[-3])
(a, b) = calculate_trc20_volumes(trc20_transactions)
print("Incoming:", a)
print("Outgoing:", b)
