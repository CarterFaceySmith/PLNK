from alpaca_trade_api.rest import REST
from alpaca.trading.client import TradingClient
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient

# Settings
API_KEY = 'PKB0OUCULGGX08VG0KW0'
SECRET_KEY = 'EpsYl1t06L03vecfmzK0aZNgcQ4JHDDWHdiSSgQU'
crypto = ['BTCUSD', 'ETHUSD', 'LTCUSD']

# Clients
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
rest_api = REST(API_KEY, SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

#Functions
def return_clients():
    return trading_client,rest_api,crypto_client,stock_client

def get_historic_data(symbol, rest_api, timeframe, start, end):
    if(symbol in crypto):
        try:
            alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
        except:
            raise(BaseException(f"Error retrieving {symbol} bars from Alpaca API"))
    else:
        try:
            alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df
        except:
            raise(BaseException(f"Error retrieving {symbol} bars from Alpaca API"))
    return alpaca_data

def liquidate_portfolio():
    print('Liquidating portfolio...')
    print(f'Starting cash: {float(rest_api.get_account().cash)}')
    rest_api.close_all_positions()
    rest_api.cancel_all_orders()
    print('Portfolio liquidated.')
    print(f'Ending cash: {float(rest_api.get_account().cash)}')

def get_portfolio_stats():
    print("Stats:")
    print(f'\tOverall portfolio value: ${float(rest_api.get_account().portfolio_value):,.2f}')
    print(f'\tCurrent buying power: ${float(rest_api.get_account().buying_power):,.2f}')
    print(f'\tCurrent equity: ${float(rest_api.get_account().equity):,.2f}')
    print(f'\tCurrent cash: ${float(rest_api.get_account().cash):,.2f}')

    print("\nPortfolio:")
    print("\tCurrent positions:")
    for pos in rest_api.list_positions():
        print(f'\t{pos.symbol}:\t{float(pos.qty):,.2f} shares')
    print("\n\tCurrent orders:")
    if len(rest_api.list_orders()) == 0:
        print('\tNo orders.')
    else:
        for order in rest_api.list_orders():
            print(f'\t{order.symbol}:\t{float(order.qty):,.2f} shares')