import asyncio
from src import config, rebalance, backtesting, testing, strategies
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def menu():
    print(f'1. Backtest a portfolio\n2. Paper rebalance\n3. Live rebalance\n4. Check live portfolio stats\n5. Exit')
    choice = input()
    match choice:
        case '1':
            strat_params = {
                'weights': {},
                'frequency': None,
            }
            tickers, target_allocations = config.input_portfolio()
            for ticker in tickers:
                if config.validate_ticker(ticker):
                    strat_params['weights'][ticker] = target_allocations[tickers.index(ticker)]
            user_start, user_end = config.input_valid_dates()
            comm, cash = config.input_comm_cash()
            strat_params['frequency'] = input("Enter rebalance rate (daily, weekly, monthly, quarterly, yearly): ")
            backtesting.backtest(strategies.Rebalance, strat_params, list(strat_params['weights'].keys()), user_start, user_end, TimeFrame.Day, cash, comm)
        case '2':
            print("Paper rebalance")
            tickers, target_allocations = config.input_portfolio()
            portfolio = dict(zip(tickers, target_allocations))
            rebalance.perform_paper_rebalance(config.rest_api, config.trading_client, desired_allocations=portfolio)
            print("Paper rebalance complete.")
            await menu()
        case '3':
            print("Live rebalance")
            tickers, target_allocations = config.input_portfolio()
            portfolio = dict(zip(tickers, target_allocations))
            await rebalance.perform_live_rebalance(trading_client=config.live_client, desired_allocations=portfolio)
            print("Live rebalance complete.")
            await menu()
        case '4':
            print(config.return_portfolio_stats(client=config.live_client))
            await menu()
        case '5':
            exit(0)
        case '6':
            print("Testing")
            await config.send_update_msg()
            # await testing.test()
            # y = config.live_client.get_all_positions()
            # for z in y:
            #     print(z)
            exit()
            await menu()
        case _:
            print('Invalid input')
            await menu()

async def main():
    input("Welcome. Press enter to continue.")
    input("Stocks are input as their ticker symbols (e.g. VOO, AAPL)\nCryptocurrencies are input as their currency pairs (e.g. BTC-USD, ETH-USD)\n")
    await menu()
    
# async def main():
#     print("Welcome.")
#     print(f'System mode: {config.SYSTEM_MODE}\n')
#     mode = input("What would you like to do?\n\t1. Backtest/Optimise\n\t2. Rebalance\n\t3. Liquidate portfolio\n\t4. Check stats\n\t5. Change API keys for this session\n\t6. Change system trading mode\n\t7. Exit\n\t8. Testing\n\t9. ACTUAL REBALANCE\n")

#     match mode:
#         case "1":
#             bt_opt_mode = input("Select your mode:\n\t1. Backtest\n\t2. Optimise\n")
#             match bt_opt_mode:
#                 case "1":
#                     backtesting.bt_opt_init(mode='BACKTEST')
#                 case "2":
#                     backtesting.bt_opt_init(mode='OPTIMISE')
#                 case _:
#                     raise ValueError("Invalid input")
#             menu()
                
#         case '2':
#             tickers, target_allocations = config.input_portfolio()
#             portfolio = dict(zip(tickers, target_allocations))

#             if input("Confirm rebalance? (y/n)") == 'y':
#                 rebalance.perform_rebalance(t_client=config.trading_client, desired_allocations=portfolio)
            
#             menu()

#         case '3':
#             # TODO; Add validation of timing, cannot liquidate if markets are not open for some assets
#             if input("Confirm liquidation of portfolio positions? (y/n)") == 'y':
#                 config.liquidate_portfolio()
#             menu()

#         case '4':
#             config.get_portfolio_stats(client=config.rest_api)
#             menu()

#         case '5':
#             config.API_KEY = input("Enter your new API primary key: \n")
#             config.SECRET_KEY = input("Enter your new API secret key: \n")
#             menu()

#         case '6':
#             print(f'Current system mode: {config.SYSTEM_MODE}\n')
#             mode_pick = input("Choose new system mode (defaults to paper):\n\t1. Paper\n\t2. Live\n")
#             match mode_pick:
#                 case '1':
#                     config.SYSTEM_MODE = 'PAPER'
#                 case '2':
#                     config.SYSTEM_MODE = 'LIVE'
#                 case _:
#                     raise ValueError("Invalid input")
#             menu()

#         case '7':
#             print("Goodbye.")
#             exit(0)

#         case '8':
#             await testing.test()

#         case '9':
#             portfolio = {'VOO': 0.4, 'VOOG': 0.15, 'BTC-USD': 0.2, 'ETH-USD': 0.2}
            
#             if input("CONFIRM REBALANCE - THIS IS ACTUAL MONEY (YES/NO)") == 'YES':
#                     client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=False)
#                     rebalance.perform_rebalance(t_client=client, desired_allocations=portfolio)
#                     await config.send_update_msg()
#             menu()

#         case _:
#             raise BaseException("Invalid input or crash")
        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())