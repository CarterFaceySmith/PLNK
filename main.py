from src import config, rebalance, backtesting
import re

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

def main():
    print("Welcome.")
    print(f'System mode: {config.SYSTEM_MODE}\n')
    mode = input("What would you like to do?\n\t1. Backtest/Optimise\n\t2. Rebalance\n\t3. Liquidate portfolio\n\t4. Check stats\n\t5. Change API keys for this session\n\t6. Change system trading mode\n\t7. Exit\n")

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
            tickers = input("Enter the desired portfolio ticker(s) separated by commas: ").split(',')
            allocation_input = input("Enter the target allocations for each ticker separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
            target_allocations = [float(x) for x in allocation_input]

            if sum(target_allocations) > 1 or sum(target_allocations) < 0:
                raise ValueError("The sum of your allocations must be between 0 and 1")

            for ticker in tickers:
                if not re.match(r'[A-Z]{3,6}', ticker):
                    raise ValueError(f"{ticker} is invalid")
                
            portfolio = dict(zip(tickers, target_allocations))
            prec = int(input("Enter the decimal precision of the rebalance (defaults to 3 if none entered): "))

            confirmation = input("Confirm rebalance? (y/n)")
            if confirmation == 'y':
                rebalance.perform_rebalance(portfolio, prec)
            
            menu()

        case '3':
            # TODO; Add validation of timing, cannot liquidate if markets are not open for some assets
            confirm = input("Confirm liquidation of portfolio positions? (y/n)")
            if confirm == 'y':
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

        case _:
            raise BaseException("Invalid input or crash")
        
if __name__ == '__main__':
    main()