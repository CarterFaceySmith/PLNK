import backtrader as bt
from alpaca.data.timeframe import TimeFrame
from src import config, strategies
import datetime, collections, re
from dateutil.relativedelta import relativedelta
import numpy as np
collections.Iterable = collections.abc.Iterable

rest_api = config.rest_api

def bt_opt_init(mode=''):
    print("Available strategies:")
    strategy = strategies.select_strat()
    strat_params = {}

    if mode == 'BACKTEST':
        for param in strategy.params._getkeys():
            strat_params[param] = input(f"input the value of the '{param}' parameter: ")

        tickers = input("Enter the desired portfolio ticker(s) separated by commas: ").split(',')
        allocation_input = input("Enter the target allocations for each ticker separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
        target_allocations = [float(x) for x in allocation_input]
        for val in target_allocations:
            if val < 0:
                raise ValueError("Target allocations must be positive")
            elif val > 1:
                raise ValueError("Target allocations must be less than 1.0")

        if sum(target_allocations) > 1 or sum(target_allocations) < 0:
            raise ValueError("The sum of your allocations must be between 0 and 1")

        for ticker in tickers:
            if len(ticker) > 4:
                raise ValueError(f"Tickers must be 4 characters or less, {ticker} is invalid")
            else:
                strat_params[ticker] = target_allocations[tickers.index(ticker)]


        user_start = input("Enter a start date for backtesting (format: yyyy-mm-dd): ")
        user_end = input("Enter an end date for backtesting (format: yyyy-mm-dd): ")
        comm = float(input("Enter the per-trade commission fee (e.g. 0.1): "))

        if user_end < user_start:
            raise ValueError("End date must be after the start date")
        
        cash = int(input("Enter the starting cash amount: "))
        plot_input = input("Would you like to plot the results? (y/n): ")
        plot = True if plot_input == 'y' else False
        
        backtest(strategy, strat_params, tickers, user_start, user_end, TimeFrame.Day, cash, comm, plot)
    
    if mode == 'OPTIMISE':  
        for param in strategy.params._getkeys():
            opt_param = input(f"Would you like to optimise the '{param}' parameter? (y/n): ")
            if opt_param == 'y':
                lower = int(input(f"input the lower bound of the '{param}' parameter: "))
                upper = int(input(f"input the upper bound of the '{param}' parameter: "))
                step = int(input(f"input the step size of the '{param}' parameter: "))
                strat_params[param] = np.linspace(lower, upper, step)
            else:
                strat_params[param] = input(f"input the value of the '{param}' parameter: ")

        tickers = input("Enter the desired portfolio ticker(s) separated by commas: ").split(',')
        allocation_input = input("Enter the target allocations for each ticker separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
        target_allocations = [float(x) for x in allocation_input]
        for val in target_allocations:
            if val < 0:
                raise ValueError("Target allocations must be positive")
            elif val > 1:
                raise ValueError("Target allocations must be less than 1.0")

        if sum(target_allocations) > 1 or sum(target_allocations) < 0:
            raise ValueError("The sum of your allocations must be between 0 and 1")

        for ticker in tickers:
            if re.match(r'[A-Z]{6}', ticker):
                raise ValueError(f"{ticker} is invalid")
            else:
                opt_ticker = input(f"Would you like to optimise the '{ticker}' allocation? (y/n): ")
                if opt_ticker == 'y':
                    lower = int(input(f"input the lower bound of the '{ticker}' allocation: "))
                    upper = int(input(f"input the upper bound of the '{ticker}' allocation: "))
                    step = int(input(f"input the step size of the '{ticker}' allocation: "))
                    strat_params[ticker] = np.linspace(lower, upper, step)
                else:
                    strat_params[ticker] = target_allocations[tickers.index(ticker)]

        user_start = input("Enter a start date for backtesting (format: yyyy-mm-dd): ")
        user_end = input("Enter an end date for backtesting (format: yyyy-mm-dd): ")
        comm = float(input("Enter the per-trade commission fee (e.g. 0.1): "))

        if user_end < user_start:
            raise ValueError("End date must be after the start date")
        
        cash = int(input("Enter the starting cash amount: "))
        plot_input = input("Would you like to plot the results? (y/n): ")
        plot = True if plot_input == 'y' else False
        
        optimise(strategy, strat_params, tickers, user_start, user_end, TimeFrame.Day, cash, comm, plot)

'''
    Backtest function intakes:
        - The strategy to test, an instance of a defined backtrader.strategy object
        - A dictionary of parameters to utilise in the strategy
        - A list of tickers whose data to retrieve for analysis
        - A start and end date as a string of form 'yyyy-mm-dd'
        - A TimeFrame interval, either day, month or year to retrieve the tickers' bars
        - The initial capital amount to test on as an integer, defaulting to 100,000
        - The commission fee per trade as a float, defaulting to 0.0
        - A boolean switch for if you want to display a chart of results upon completion
'''
def backtest(strategy, strat_params=None, symbols=list, start="2016-06-01", end="2023-02-01", timeframe=TimeFrame.Day, cash=100000, comm=0.0, plotting=bool):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    
    for symbol in symbols:
        alpaca_data = config.get_historic_data(symbol, rest_api, timeframe, start, end)
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)
        print(f'Added {symbol} data to cerebro instance\n')
        print(f"{alpaca_data.head(3)}\n")

    cerebro.broker.setcommission(commission=comm)
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run(maxcpus=1)
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value:,.2f} ---> Return: {((final_portfolio_value/initial_portfolio_value - 1)*100):,.2f}%')
    difference_in_years = relativedelta(datetime.datetime.strptime(end, "%Y-%m-%d"), datetime.datetime.strptime(start, "%Y-%m-%d")).years
    print(f'Average Annualised Return: {(((final_portfolio_value/initial_portfolio_value - 1)*100)/difference_in_years):,.2f}%')

    # strat = results[0]
    # sharpe_rat = strat.analyzers.mysharpe.get_analysis()['sharperatio']
    # print(f'Sharpe Ratio: {sharpe_rat:.2f}')
    if plotting:
        cerebro.plot()

'''
    Optimise function intakes:
        - The strategy to test, an instance of a defined backtrader.strategy object
        - A dictionary of parameters to utilise in the strategy in the form of ranges to optimise for, this is then dereferenced/'unpacked' in the optstrategy call using **
        - A list of tickers whose data to retrieve for analysis
        - A start and end date as a string of form 'yyyy-mm-dd'
        - A TimeFrame interval, either day, month or year to retrieve the tickers' bars
        - The initial capital amount to test on as an integer, defaulting to 100,000
        - The commission fee per trade as a float, defaulting to 0.0
        - A boolean switch for if you want to display a chart of results upon completion
'''
def optimise(strategy, strat_params=None, symbols=list, start="2016-06-01", end="2023-02-01", timeframe=TimeFrame.Day, cash=100000, comm=0.0, plotting=bool):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.optstrategy(strategy, **strat_params)
    
    for symbol in symbols:
        alpaca_data = config.get_historic_data(symbol, rest_api, timeframe, start, end)
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)
        print(f'Added {symbol} data to cerebro instance\n')
        print(f"{alpaca_data.head(3)}\n")
    
    cerebro.broker.setcommission(commission=comm)
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value:,}')
    results = cerebro.run(maxcpus=1)
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value:,.2f} ---> Return: {((final_portfolio_value/initial_portfolio_value - 1)*100):,.2f}%')
    difference_in_years = relativedelta(datetime.datetime.strptime(end, "%Y-%m-%d"), datetime.datetime.strptime(start, "%Y-%m-%d")).years
    print(f'Average Annualised Return: {(((final_portfolio_value/initial_portfolio_value - 1)*100)/difference_in_years):,.2f}%')
    if plotting:
        cerebro.plot()

# weights = {"VOO":0.5}
# tickers = list(weights.keys())
# user_start = "2016-06-01"
# user_end = "2023-02-01"

# strat_params = {'frequency': 'monthly',
#                 'VOO': 0.2,
#                 'AAPL': 0.2,
#                 }

# E.g. strat_params['VOO'] = np.linspace(0,1,10)
# NOTE: To feed a decimal point range into optimise for some parameter a numpy linspace must be used as above to avoid potential rounding errors, the standard range() function does't fucking work for floats

# optimise(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
# backtest(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
# backtest(strategies.ETHScalping, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)