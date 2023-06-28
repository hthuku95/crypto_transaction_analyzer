from datetime import datetime, timedelta
from utils import fetch_ethereum_transactions
from web3 import Web3

# Ethereum address
ethereum_address = "0xdB3c617cDd2fBf0bb4309C325F47678e37F096D9"
ETHERSCAN_API_KEY = "K9XBVRXWXPGQGRT8JXV3DU8E2UPMYIUVP7"

transactions = fetch_ethereum_transactions("0xDAFEA492D9c6733ae3d56b7Ed1ADB60692c98Bc5",ETHERSCAN_API_KEY )

def calculate_eth_volumes(transactions):
    incoming_volume = 0
    outgoing_volume = 0

    # Calculate the timestamp 60 days ago
    cutoff_date = int((datetime.now() - timedelta(days=60)).timestamp())

    print(transactions)
    for tx in transactions:
        value = float(tx['value']) / 10 ** 18  # Convert value from wei to ether
        print("Value:",value)
        timestamp = int(tx['timeStamp'])
        print("timestamp:",timestamp)
        print("cutoff_date:",cutoff_date)

        if timestamp >= cutoff_date:
            if tx['from'] == ethereum_address:
                outgoing_volume += value
            if tx['to'] == ethereum_address:
                incoming_volume += value

    return incoming_volume, outgoing_volume


(a ,b) = calculate_transaction_volumes(transactions)
print(a)
print(b)