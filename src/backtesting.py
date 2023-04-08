import backtrader as bt
from alpaca.data.timeframe import TimeFrame
from src import config, strategies
import datetime, collections
from dateutil.relativedelta import relativedelta
import numpy as np
collections.Iterable = collections.abc.Iterable

rest_api = config.rest_api

def bt_opt_init(mode=''):
    print("Available strategies:")
    strategy = strategies.select_strat()
    strat_params = {}

    if mode == 'BACKTEST':
        # for param in strategy.params._getkeys():
        #     strat_params[param] = input(f"Input the value of the '{param}' parameter: ")

        tickers, target_allocations = config.input_portfolio()

        for ticker in tickers:
            if config.validate_ticker(ticker):
                strat_params[ticker] = target_allocations[tickers.index(ticker)]

        user_start, user_end = config.input_valid_dates()
        comm, cash = config.input_comm_cash()
        plot = config.input_plotting()
        
        backtest(strategy, strat_params, tickers, user_start, user_end, TimeFrame.Day, cash, comm, plot)
    
    if mode == 'OPTIMISE':  
        for param in strategy.params._getkeys():
            opt_param = input(f"Would you like to optimise the '{param}' parameter? (y/n): ")
            if opt_param == 'y':
                lower = int(input(f"Input the lower bound of the '{param}' parameter: "))
                upper = int(input(f"Input the upper bound of the '{param}' parameter: "))
                step = int(input(f"Input the step size of the '{param}' parameter: "))
                strat_params[param] = np.linspace(lower, upper, step)
            else:
                strat_params[param] = input(f"Input the value of the '{param}' parameter: ")

        tickers, target_allocations = config.input_portfolio()

        for ticker in tickers:
            if config.validate_ticker(ticker):
                opt_ticker = input(f"Would you like to optimise the '{ticker}' allocation? (y/n): ")
                if opt_ticker == 'y':
                    lower = int(input(f"Input the lower bound of the '{ticker}' allocation: "))
                    upper = int(input(f"Input the upper bound of the '{ticker}' allocation: "))
                    step = int(input(f"Input the step size of the '{ticker}' allocation: "))
                    strat_params[ticker] = np.linspace(lower, upper, step)
                else:
                    if ticker in strategy.params._getkeys():
                        # NOTE: If the ticker is explicitly defined in the preset params then we set it, if not then it is passed over
                        strat_params[ticker] = target_allocations[tickers.index(ticker)]

        user_start, user_end = config.input_valid_dates()
        comm, cash = config.input_comm_cash()
        plot = config.input_plotting()
        
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
def backtest(strategy, strat_params=None, symbols=list, start="2015-12-01", end="2023-02-10", timeframe=TimeFrame.Day, cash=100000, comm=0.0, plotting=bool):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    
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
def optimise(strategy, strat_params=None, symbols=list, start="2015-12-01", end="2023-02-10", timeframe=TimeFrame.Day, cash=100000, comm=0.0, plotting=bool):
    cerebro = bt.Cerebro(stdstats=True, optreturn=False)
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
# NOTE: To feed a decimal point range into optimise for some parameter a numpy linspace must be used as above to avoid potential rounding errors, the standard range() function does't fucking work for floats, note that the 'step' param of this is not the step size but the step number
# NOTE: For other numbers range() is the better choice, for example sma_period can cause complications if a linspace is used
def test():
    # optimise(strategies.ETHScalping, {
    #         "buy_threshold": np.linspace(500,600,3),
    #         "sell_threshold": np.linspace(900,1000,3),
    #         "sma_period": range(10,20)
    #     }, ['ETHUSD'], '2015-06-01', '2023-02-10', TimeFrame.Day, 10000, 0.0, False)

    # strat_params = {
    #     'frequency': 'monthly',
    #     'weights': {
    #         'MSFT': 0.3,
    #         'AAPL': 0.3,
    #     },
    # }

    # params = {
    #     'period': range(14,65),
    # }

    # optimise(strategies.SimpleSMA, params, ['ETHUSD'], '2015-01-01', '2023-01-01', TimeFrame.Day, 10000, 0.0, False)
    # optimise(strategies.Rebalance, params, ['MSFT', 'AAPL'], '2020-01-01', '2023-01-01', TimeFrame.Day, 10000, 0.0, False)
# optimise(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
# backtest(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
# backtest(strategies.ETHScalping, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)