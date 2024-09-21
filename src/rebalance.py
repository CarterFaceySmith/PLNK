from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from src import config

## TODO: Combine the two rebalance funcs
'''
The perform_live_rebalance function intakes:
    - trading_client: the live TradingClient object
    - desired_allocations: a dictionary of ticker: allocation pairs
    - precision: the number of decimal places to round to

The function will close all positions and open orders, then submit market orders for each ticker in the desired allocations dictionary to the live client.

async def perform_live_rebalance(trading_client, desired_allocations, precision=3):
    print('Closing all positions and open orders')
    trading_client.close_all_positions(cancel_orders=True)
    print('Beginning rebalance')
    available_cash = float(trading_client.get_account().cash)
    print(f'Available cash: {available_cash}')

    dollar_value_allocations = {symbol: percent * available_cash for symbol, percent in desired_allocations.items()}

    for symbol, dollars_alloc in dollar_value_allocations.items():
        market_order_data, qty = config.construct_market_order(symbol, dollars_alloc, 'BUY', precision)
        
        print(f"Submitting market order for {qty} units of {symbol}")
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                        )
        print(f"Order submitted: {market_order.qty} units of {market_order.symbol}")

    print("All orders submitted.")
    await config.send_update_msg()
'''

async def perform_live_rebalance(trading_client, desired_allocations, precision=3):
    print('Closing all positions and open orders')
    await config.send_message('Closing all positions and open orders')
    trading_client.close_all_positions(cancel_orders=True)
    print('Beginning rebalance')
    await config.send_message('Beginning rebalance')
    available_cash = float(trading_client.get_account().cash)
    print(f'Available cash: {available_cash}')
    await config.send_message(f'Available cash: {available_cash}')

    dollar_value_allocations = {symbol: percent * available_cash for symbol, percent in desired_allocations.items()}

    for symbol, dollars_alloc in dollar_value_allocations.items():
        market_order_data, qty = config.construct_market_order(symbol, dollars_alloc, 'BUY', precision)
        if (symbol in config.crypto):
            market_order_data = MarketOrderRequest(symbol=symbol, notional=dollars_alloc, side='buy', time_in_force='gtc')
        else:
            market_order_data, qty = config.construct_market_order(symbol, dollars_alloc, 'BUY', precision)

        print(f"Submitting market order for {qty} units of {symbol}")
        await config.send_message(f"Submitting market order for {symbol}")
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                        )
        print(f"Order submitted: {market_order.qty} units of {market_order.symbol}")
        await config.send_message(f"Order submitted: {market_order.qty} units of {market_order.symbol}\n")

    print("All orders submitted.")
    await config.send_message("All orders submitted.")
    await config.send_update_msg()

'''
The perform_paper_rebalance function intakes:
    - rest_api: the rest API object
    - trading_client: the paper TradingClient object
    - desired_allocations: a dictionary of ticker: allocation pairs
    - precision: the number of decimal places to round to

The function will close all positions and open orders, then submit market orders for each ticker in the desired allocations dictionary to the paper client.
'''
def perform_paper_rebalance(rest_api, trading_client, desired_allocations, precision=3):
    print('Closing all positions and open orders')
    trading_client.close_all_positions(cancel_orders=True)
    print('Beginning rebalance')
    available_cash = float(rest_api.get_account().cash)
    print(f'Available cash: {available_cash}')

    dollar_value_allocations = {symbol: percent * available_cash for symbol, percent in desired_allocations.items()}

    for symbol, dollars_alloc in dollar_value_allocations.items():
        market_order_data, qty = config.construct_market_order(symbol, dollars_alloc, 'BUY', precision)
        
        print(f"Submitting market order for {qty} units of {symbol}")
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                        )
        print(f"Order submitted: {market_order.qty} units of {market_order.symbol}\n")

    print("All orders submitted.")
