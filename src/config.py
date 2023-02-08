from alpaca_trade_api.rest import REST
from alpaca.trading.client import TradingClient
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient

# Settings
API_KEY = 'PKB0OUCULGGX08VG0KW0'
SECRET_KEY = 'EpsYl1t06L03vecfmzK0aZNgcQ4JHDDWHdiSSgQU'
crypto = ['BTCUSD', 'ETHUSD']

# Clients
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
rest_api = REST(API_KEY, SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

#Functions
def return_clients():
    return trading_client,rest_api,crypto_client,stock_client