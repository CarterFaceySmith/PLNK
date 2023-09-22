from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from src import config

'''
The perform_rebalance function intakes:
    Parameter 1: A dictionary of Alpaca API tickers and corresponding percentage allocations (0 < sum(x) < 1)
    Parameter 2: An integer to set the decimal precision of the orders
'''
async def perform_live_rebalance(trading_client, desired_allocations, precision=3):
    print('Closing all positions')
    config.liquidate_portfolio(client=trading_client)
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
        print(f"Order submitted: {market_order.qty} units of {market_order.symbol}\n")

    print("All orders submitted.")
    await config.send_update_msg()


def perform_paper_rebalance(rest_api, trading_client, desired_allocations, precision=3):
    print('Closing all positions')
    rest_api.close_all_positions()
    print('Cancelling all open orders')
    rest_api.cancel_all_orders()
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