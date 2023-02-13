from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import config

trading_client, rest_api, crypto_client, stock_client = config.return_clients()

# def get_pause():
    # now = datetime.now()
    # next_day = now.replace(second=0, microsecond=0) + timedelta(days=1)
    # pause = math.ceil((next_day - now).seconds)
    # print(f"Sleep for {pause}")
    # return pause

'''
The rebalance function intakes:
    Parameter 1: A dictionary of Alpaca API tickers and corresponding percentage allocations (0 < sum(x) < 1)
    Parameter 2: An integer to set the decimal precision of the orders
'''
def perform_rebalance(desired_allocations, precision=3):
    rest_api.close_all_positions()
    rest_api.cancel_all_orders()

    available_cash = float(rest_api.get_account().cash)

    dollar_value_allocations = {symbol: percent * available_cash for symbol, percent in desired_allocations.items()}

    # Rebalance
    for symbol, dollars_alloc in dollar_value_allocations.items():
        if symbol in config.crypto:
            time_in_force = TimeInForce.GTC
        else:
            time_in_force = TimeInForce.DAY

        if symbol in config.crypto:
            market_price = rest_api.get_latest_crypto_bar(symbol, exchange='FTXU').c
        else:
            market_price = rest_api.get_latest_bar(symbol).c

        target_holdings = round(dollars_alloc / market_price, precision)

        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=target_holdings,
            side=OrderSide.BUY,
            time_in_force=time_in_force
        )

        print(f"Submitting market order for {target_holdings} units of {symbol}")
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                        )
        print(f"Order submitted: {market_order.qty} units of {market_order.symbol}\n")

    print("All orders submitted.")

# percent_allocations = { "BTCUSD" : 0.1 , "ETHUSD" : 0.05, "VOO" : 0.25, "VOOG" : 0.40, "MSFT" : 0.1}
# perform_rebalance(percent_allocations)
# time.sleep(get_pause())