# crypto_transaction_analyzer

A Python Script for extracting transaction histories of wallet addresses from different Blockchain networks for analysis purposes

## Prerequisites

Please install or have installed the following:

- [python](https://www.python.org/downloads/)

## Installation and Configuration

1. Set up a virtual environment and activate it
2. Clone this repo

```bash
git clone https://github.com/hthuku95/crypto_transaction_analyzer.git
```

3. Install all requirements

```bash
pip install -r requirements.txt
```
## API Keys
create a .env file and configure the following API keys:
```bash
BITCOIN_EXPLORER_API_KEY = "Your Blockcypher API Key"
CRYPTO_COMPARE_API_KEY = "Your CryptoCompare API Key"
BSCSCAN_API_KEY = "Your Bsscan API Key"
ETHERSCAN_API_KEY = "Your Etherscan API Key"
TRONSCAN_API_KEY = "Your TronGrid API Key"
```
## Quickstart
1. Cd into the scripts folder and run:

```
python bitcoin.py 
python bnb.py
python busd.py
python erc20.py
python ethereum.py
python trc20.py
```
