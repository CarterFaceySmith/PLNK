import asyncio
from src import config, rebalance, backtesting, testing
from alpaca.trading.client import TradingClient
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def menu():
    choice = input('1. Main menu\n2. Exit\n')
    match choice:
        case '1':
            main()
        case '2':
            print('Goodbye.')
            exit(0)
        case _:
            raise ValueError('Invalid input')

async def main():
    print("Welcome.")
    print(f'System mode: {config.SYSTEM_MODE}\n')
    mode = input("What would you like to do?\n\t1. Backtest/Optimise\n\t2. Rebalance\n\t3. Liquidate portfolio\n\t4. Check stats\n\t5. Change API keys for this session\n\t6. Change system trading mode\n\t7. Exit\n\t8. Testing\n\t9. ACTUAL REBALANCE\n")

    match mode:
        case "1":
            bt_opt_mode = input("Select your mode:\n\t1. Backtest\n\t2. Optimise\n")
            match bt_opt_mode:
                case "1":
                    backtesting.bt_opt_init(mode='BACKTEST')
                case "2":
                    backtesting.bt_opt_init(mode='OPTIMISE')
                case _:
                    raise ValueError("Invalid input")
            menu()
                
        case '2':
            tickers, target_allocations = config.input_portfolio()
            portfolio = dict(zip(tickers, target_allocations))

            if input("Confirm rebalance? (y/n)") == 'y':
                rebalance.perform_rebalance(portfolio)
            
            menu()

        case '3':
            # TODO; Add validation of timing, cannot liquidate if markets are not open for some assets
            if input("Confirm liquidation of portfolio positions? (y/n)") == 'y':
                config.liquidate_portfolio()
            menu()

        case '4':
            config.get_portfolio_stats()
            menu()

        case '5':
            config.API_KEY = input("Enter your new API primary key: \n")
            config.SECRET_KEY = input("Enter your new API secret key: \n")
            menu()

        case '6':
            print(f'Current system mode: {config.SYSTEM_MODE}\n')
            mode_pick = input("Choose new system mode (defaults to paper):\n\t1. Paper\n\t2. Live\n")
            match mode_pick:
                case '1':
                    config.SYSTEM_MODE = 'PAPER'
                case '2':
                    config.SYSTEM_MODE = 'LIVE'
                case _:
                    raise ValueError("Invalid input")
            menu()

        case '7':
            print("Goodbye.")
            exit(0)

        case '8':
            await testing.test()

        case '9':
            portfolio = {'VOO': 0.4, 'VOOG': 0.15, 'BTC-USD': 0.2, 'ETH-USD': 0.2}
            
            if input("CONFIRM REBALANCE - THIS IS ACTUAL MONEY (YES/NO)") == 'YES':
                    client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=False)
                    rebalance.perform_rebalance(t_client=client, desired_allocations=portfolio)
                    await config.send_update_msg()
            menu()

        case _:
            raise BaseException("Invalid input or crash")
        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())