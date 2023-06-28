from utils import fetch_transaction_data
from csv_exporter import export_to_csv
from charts_generator import generate_transaction_charts

def main():
    # Wallet addresses for different asset types (excluding ERC-20)
    wallet_addresses = {
        'TRC-20': 'TR9octGKwGi8EaBhphP8d8D6dTkSyMJKXW',
        'ETH': '0xdB3c617cDd2fBf0bb4309C325F47678e37F096D9',
        'BNB': '0x3F10a43438cdF6B0E9Ef39dcA5F9438dd3326227',
        'BUSD': '0x4aA51fa0dE0e94e801D7E78f94E15c5D15133454',
        'BTC': [
            'Bc1qzh8rga4vvvzzdan5jqhz5ljygt0hvdp7j74qzn',
            '1GrwDkr33gT6LuumniYjKEGjTLhsL5kmqC'
        ]
    }

    # Call the function to fetch transaction data
    transaction_data = fetch_transaction_data(wallet_addresses)

    # Perform further processing and analysis as per your requirements
    # ...

    # Export transaction data to a CSV file
    export_to_csv(transaction_data)

    # Generate transaction charts
    generate_transaction_charts(transaction_data)

if __name__ == '__main__':
    main()