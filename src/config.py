from alpaca_trade_api.rest import REST
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
import re, datetime

# Settings
SYSTEM_MODE = 'PAPER'
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
    print(f'Starting cash: {float(rest_api.get_account().cash):,.2f}')
    rest_api.cancel_all_orders()
    rest_api.close_all_positions()
    print('Portfolio liquidated.')
    print(f'Ending cash: {float(rest_api.get_account().cash):,.2f}')

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

def validate_ticker(input=''):
    if re.match(r'[A-Z]{3,6}', input):
        return True
    else: 
        raise ValueError(f'{input} is an invalid ticker')
    
def validate_allocations(allocations=list[float]):
    for val in allocations:
            if (val < 0.0) or (val > 1.0):
                raise ValueError("Target allocations must be between 0.0 and 1.0, {val} is an invalid input")

    if (sum(allocations) > 1.0) or (sum(allocations) < 0.0):
        raise ValueError("The sum of your allocations must be between 0.0 and 1.0")
    
    else:
        print(f'Your target allocations appear to be valid')
    
def input_valid_dates():
    curr_date = datetime.datetime.today()
    user_start = input("Enter a start date for testing (format: yyyy-mm-dd): ")
    user_end = input("Enter an end date for testing: (format: yyyy-mm-dd): ")
    val_start = datetime.datetime.strptime(user_start, "%Y-%m-%d")
    val_end = datetime.datetime.strptime(user_end, "%Y-%m-%d")

    if (val_start.year < 1950) or (val_start.year > curr_date.year):
        raise ValueError(f'The start date must be between 1950-01-01 and today\'s date: {curr_date}')
    elif (val_end > curr_date):
        raise ValueError('The end date must be before today\'s date: {curr_date}')
    elif user_end < user_start:
            raise ValueError("End date must be after the start date")
    else:
        return user_start, user_end

def input_portfolio():
    tickers = input("Enter the desired portfolio ticker(s) separated by commas: ").split(',')
    allocation_input = input("Enter the target allocations for each ticker separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
    target_allocations = [float(x) for x in allocation_input]
    validate_allocations(target_allocations)

    return tickers, target_allocations

def input_comm_cash():
    comm = float(input("Enter the per-trade commission fee (e.g. 0.1): "))
    if (comm < 0.0) or (comm > 100.0):
        raise ValueError('The value for per-trade commision should be somewhere between 0.0 and 100.0, this depends on your broker')
    cash = int(input("Enter the starting cash amount: "))
    if (cash < 0.0):
        raise ValueError('The starting cash amount cannot be negative')
    else:
        return comm, cash

def input_plotting():
    # plot_input = input("Would you like to plot the results? (y/n): ")
    # TODO: There is an active bug with Backtrader that renders plotting via matplotlib impossible for now, this will be set to always returns False until the bug is fixed
    # return True if plot_input == 'y' else False
    return False

def construct_market_order(symbol,allocation,order_side='',prec=3):
    if symbol in crypto:
        time_in_force = TimeInForce.GTC # Required for crypto market orders
        market_price = rest_api.get_latest_crypto_bar(symbol, exchange='CBSE').c
    else:
        time_in_force = TimeInForce.DAY # Can be changed
        market_price = rest_api.get_latest_bar(symbol).c
    
    target_holding = round(allocation / market_price, prec)

    if order_side == 'SELL':
        construct_side = OrderSide.SELL
    elif order_side == 'BUY':
        construct_side = OrderSide.BUY
    else:
        ValueError('Invalid order side input')
    
    market_order = MarketOrderRequest(
            symbol=symbol,
            qty=target_holding,
            side=construct_side,
            time_in_force=time_in_force
        )
    
    return market_order, target_holding

def check_sys_mode():
    #   TODO: Implement change of API keys per mode 
    if SYSTEM_MODE == 'PAPER':
        pass
    elif SYSTEM_MODE == 'LIVE':
        pass
    return SYSTEM_MODE