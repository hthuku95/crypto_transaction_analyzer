from utils import (
    fetch_ethereum_transactions,
    fetch_erc20_transactions,
    fetch_busd_transactions,
    fetch_bitcoin_transactions,
    fetch_bnb_transactions,
    fetch_trc20_transactions,
    calculate_bitcoin_volumes,
    calculate_eth_volumes,
    calculate_bnb_volumes,
    calculate_busd_volumes,
    calculate_erc20_volumes,
    calculate_trc20_volumes
)
from csv_exporter import export_to_csv
from charts_generator import generate_transaction_charts

COIN_MARKET_CAP_API_KEY = "5662e1f7-7758-49c3-82a7-9569fb9ea99c"

ETHERSCAN_API_KEY = "K9XBVRXWXPGQGRT8JXV3DU8E2UPMYIUVP7"
BSCSCAN_API_KEY = "Y5VBBSWUKS4VIZ6S1HCKVCW27XK7VU8X9J"
TRONSCAN_API_KEY = "60003d7a-10cd-4d0c-9abe-5a781c1971c2"
BITCOIN_EXPLORER_API_KEY = ""

ethereum_address = "0xdB3c617cDd2fBf0bb4309C325F47678e37F096D9"
bnb_address = "0x3F10a43438cdF6B0E9Ef39dcA5F9438dd3326227"
btc_address_one = "Bc1qzh8rga4vvvzzdan5jqhz5ljygt0hvdp7j74qzn"
btc_address_two = "1GrwDkr33gT6LuumniYjKEGjTLhsL5kmqC"
busd_address = "0x4aA51fa0dE0e94e801D7E78f94E15c5D15133454"
trc20_address = "TR9octGKwGi8EaBhphP8d8D6dTkSyMJKXW"
erc20_address_one = "0xd9ba1Dbe38eB76307ec275F11CEd907033961bA1"
erc20_address_two = "0x4F196FdEdC51C7F0c9E33D1D9030d8EC5C5A238C"
erc20_address_three = "0x36928500bc1dcd7af6a2b4008875cc336b927d57"

def main():
    # Call the function to fetch transaction data
    eth_transactions = fetch_ethereum_transactions(ethereum_address,ETHERSCAN_API_KEY)
    bnb_transactions = fetch_bnb_transactions(bnb_address,BSCSCAN_API_KEY)
    btc_one_transactions = fetch_bitcoin_transactions(btc_address_one,BITCOIN_EXPLORER_API_KEY)
    btc_two_transactions = fetch_bitcoin_transactions(btc_address_two,BITCOIN_EXPLORER_API_KEY)
    busd_transactions = fetch_busd_transactions(busd_address,BSCSCAN_API_KEY)
    bnb_transactions = fetch_bnb_transactions(bnb_address,BSCSCAN_API_KEY)
    erc20_one_transactions = fetch_erc20_transactions(erc20_address_one,ETHERSCAN_API_KEY)
    erc20_two_transactions = fetch_erc20_transactions(erc20_address_two,ETHERSCAN_API_KEY)
    erc20_three_transactions = fetch_erc20_transactions(erc20_address_three,ETHERSCAN_API_KEY)
    trc20_transactions = fetch_erc20_transactions(trc20_address,TRONSCAN_API_KEY)


    # Export transaction data to a CSV file
    eth_csv = export_to_csv(eth_transactions)
    bnb_csv = export_to_csv(bnb_transactions)
    btc_one_csv = export_to_csv(btc_one_transactions)
    btc_two_csv = export_to_csv(btc_two_transactions)
    busd_csv = export_to_csv(busd_transactions)
    bnb_csv = export_to_csv(bnb_transactions)
    erc20_one_csv = export_to_csv(erc20_one_transactions)
    erc20_two_csv = export_to_csv(erc20_two_transactions)
    erc20_three_csv = export_to_csv(erc20_three_transactions)
    trc20_csv = export_to_csv(trc20_transactions)

    # Generate transaction charts
    generate_transaction_charts(transaction_data)

if __name__ == '__main__':
    main()