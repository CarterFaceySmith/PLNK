from alpaca_trade_api.rest import REST
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
import re, datetime
import yfinance as yf
import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd
from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, CallbackContext

# Settings
SYSTEM_MODE = 'PAPER'
API_KEY = 'PKB0OUCULGGX08VG0KW0'
SECRET_KEY = 'EpsYl1t06L03vecfmzK0aZNgcQ4JHDDWHdiSSgQU'
LIVE_API_KEY = 'AKQPMSXS0PF3WFVMV53K'
LIVE_SEC_KEY = '8x5QP70KmhJLz8RPtNK8GVOsUZ7lcUrvlIFbbGww'
crypto = ['BTCUSD', 'ETHUSD', 'LTCUSD', 'BTC-USD', 'ETH-USD', 'LTC-USD']

bot_token = '6376644809:AAHDbtsnmzyHCZuFrshhcs7un1-7r0g7j7M'
tg_chat_id = '6014130527'

# Clients
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
live_client = TradingClient(LIVE_API_KEY, LIVE_SEC_KEY, paper=False)
rest_api = REST(API_KEY, SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
bot = Bot(token=bot_token)

# Functions
def return_clients():
    return trading_client,rest_api,crypto_client,stock_client

async def send_message(message):
    await bot.send_message(chat_id=tg_chat_id, text=message)
    print(f'Message log: {message}')

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

def liquidate_portfolio(client):
    print('Liquidating portfolio...')
    print(f'Starting cash: {float(client.get_account().cash):,.2f}')
    client.cancel_all_orders()
    client.close_all_positions()
    print('Portfolio liquidated.')
    print(f'Ending cash: {float(client.get_account().cash):,.2f}')

# def get_portfolio_stats(client):
#     print("Stats:")
#     print(f'\tOverall portfolio value: ${float(client.get_account().portfolio_value):,.2f}')
#     print(f'\tCurrent buying power: ${float(client.get_account().buying_power):,.2f}')
#     print(f'\tCurrent equity: ${float(client.get_account().equity):,.2f}')
#     print(f'\tCurrent cash: ${float(client.get_account().cash):,.2f}')

#     # print("\nPortfolio:")
#     # print("\tCurrent positions:")
#     # for pos in client.get_all_positions():
#     #     print(f'\t{pos.symbol}:\t{float(pos.qty):,.2f} shares')
#     # print("\n\tCurrent orders:")
#     # if len(client.get_orders()) == 0:
#     #     print('\tNo orders.')
#     # else:
#     #     for order in client.get_orders():
#     #         print(f'\t{order.symbol}:\t{float(order.qty):,.2f} shares')

def return_portfolio_stats(client):
    retString = f'\n--------------------\nPortfolio stats:\nOverall portfolio value: ${float(client.get_account().portfolio_value):,.2f}\nCurrent buying power: ${float(client.get_account().buying_power):,.2f}\nCurrent equity: ${float(client.get_account().equity):,.2f}\nCurrent cash: ${float(client.get_account().cash):,.2f}\n--------------------\n'
    return retString

## TODO: Current bug retrieving account open positions from Alpaca
async def send_update_msg():
    await send_message(f"---------------------\nRebalance performed\nDate: {datetime.datetime.today().strftime('%d-%m-%Y')}{return_portfolio_stats(live_client)}")

    # pos_list = live_client.get_all_positions()
    # order_list = live_client.get_orders()
    # if len(order_list) == 0:
    #     order_list = 'No orders.'
    # await send_message(f"Portfolio:\n\tCurrent positions:\n{pos_list}\nCurrent orders: {order_list}")
    # for pos in live_client.list_positions():
    #     await send_message(f'\t\t{pos.symbol}:\t{float(pos.qty):,.2f} shares')
    # await send_message("\n\tCurrent orders:")
    # if len(live_client.list_orders()) == 0:
    #     await send_message('\t\tNo orders.')
    # else:
    #     for order in live_client.list_orders():
    #         await send_message(f'\t{order.symbol}:\t{float(order.qty):,.2f} shares')

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

def download_to_csv(symbol, start='2010-09-09', end='2023-09-01'):
    data_df = yf.download(symbol, start_date=start, end_date=end)
    data_df.to_csv(f"{symbol}_financial_data.csv")

def csv_to_df(symbol):
    data_df = pd.read_csv(f"{symbol}_financial_data.csv", index_col='Date', parse_dates=True)
    data = bt.feeds.PandasData(dataname=data_df)
    return data

def check_sys_mode():
    #   TODO: Implement change of API keys per mode 
    if SYSTEM_MODE == 'PAPER':
        pass
    elif SYSTEM_MODE == 'LIVE':
        pass
    return SYSTEM_MODE