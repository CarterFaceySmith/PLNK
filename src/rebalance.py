from datetime import datetime, timedelta
import math
import time
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api.stream import Stream
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
import src.config as config

trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)

rest_api = REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')

# no keys required.
crypto_client = CryptoHistoricalDataClient()

# keys required
stock_client = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)

crypto_symbols = {"BTCUSD", "ETHUSD"}

percent_allocations = { "BTCUSD" : 0.0825 , "ETHUSD" : 0.06, "VOO" : 0.33, "VOOG" : 0.22, "MSFT" : 0.025, "ASTS" : 0.025}

max_qty_precision = {"BTCUSD" : 4 , "ETHUSD" : 3, "VOO" : 3, "VOOG" : 3, "APPL" : 3, "MSFT" : 3, "ASTS" : 3, "GOOG" : 3 }

def get_pause():
    now = datetime.now()
    next_day = now.replace(second=0, microsecond=0) + timedelta(days=1)
    pause = math.ceil((next_day - now).seconds)
    print(f"Sleep for {pause}")
    return pause

while(True):
    
    # liquidate all existing positions and orders before rebalancing
    rest_api.close_all_positions()
    rest_api.cancel_all_orders()

    # get available cash
    available_cash = float(rest_api.get_account().cash)

    # how many dollars we want to allocate to each symbol
    dollar_value_allocations = {symbol: percent * available_cash for symbol, percent in percent_allocations.items()}

    # Rebalance portfolio
    for symbol, dollars_alloc in dollar_value_allocations.items():
        if symbol in crypto_symbols:
            time_in_force = TimeInForce.GTC
        else:
            time_in_force = TimeInForce.DAY

        # market price of current ETF
        if symbol in crypto_symbols:
            market_price = rest_api.get_latest_crypto_bar(symbol, exchange="FTXU").close
        else:
            market_price = rest_api.get_latest_bar(symbol).c

        # how many shares we want, rounded to the most allowed decimal places
        target_holdings = round(dollars_alloc / market_price, max_qty_precision[symbol])

        # how many shares we have to buy to match target
        order_quantity = target_holdings

        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=order_quantity,
            side=OrderSide.BUY,
            time_in_force=time_in_force
        )

        print(f"Submitting market order for {order_quantity} units of {symbol}")

        # Market order
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                       )

        print(f"Order submitted: {market_order}")
    
    time.sleep(get_pause())