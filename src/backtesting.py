import backtrader as bt
from alpaca.data.timeframe import TimeFrame
from src import config, strategies
import datetime, collections
from dateutil.relativedelta import relativedelta
import numpy as np
import yfinance as yf
collections.Iterable = collections.abc.Iterable

rest_api = config.rest_api

def calculate_strategy_rating(results, annual_percent_return):
    """
    Calculate a rating for the strategy based on the analyzers and returns.

    Parameters:
    results (Backtrader Strategy Results): Strategy results from backtesting.

    Returns:
    int: Strategy rating on a scale of 1 to 5.
    """

    # Extract relevant metrics from analyzers
    # annual_return = results[0].analyzers.
    sharpe_ratio = results[0].analyzers.mysharpe.get_analysis()["sharperatio"]
    sqn = results[0].analyzers.sqn.get_analysis()["sqn"]
    vwr = results[0].analyzers.vwr.get_analysis()["vwr"]

    # Define thresholds for each metric to assign ratings
    return_thresholds = [5.0, 10.0, 15.0, 20.0, 25.0]  # Annual return thresholds as a whole percentage
    sharpe_thresholds = [0.0, 0.5, 1.0, 1.5, 2.0]  # Sharpe Ratio thresholds
    sqn_thresholds = [0.0, 2.0, 2.5, 3.0, 5.1]     # SQN thresholds
    vwr_thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]     # VWR thresholds

    # Calculate ratings based on thresholds
    return_rating = sum(annual_percent_return >= threshold for threshold in return_thresholds)
    sharpe_rating = sum(sharpe_ratio >= threshold for threshold in sharpe_thresholds)
    sqn_rating = sum(sqn >= threshold for threshold in sqn_thresholds)
    vwr_rating = sum(vwr >= threshold for threshold in vwr_thresholds)

    # Calculate an overall rating as an average of individual ratings
    overall_rating = (return_rating + sharpe_rating + sqn_rating + vwr_rating) / 4

    return overall_rating

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
def backtest(strategy, strat_params=None, symbols=list, start="2000-01-01", end="2023-08-10", timeframe=TimeFrame.Day, cash=100000, comm=0.0, plotting=bool):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    # dict(**eval('dict(' + strat_params + ')'))
    cerebro.addstrategy(strategy, strat_params)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    
    for symbol in symbols:
        # alpaca_data = config.get_historic_data(symbol, rest_api, timeframe, start, end)
        alpaca_data = yf.download(symbol, start=start, end=end)
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)
        print(f'Added {symbol} data to cerebro instance\n')
        print(f"{alpaca_data.head(1)}\n")

    cerebro.broker.setcommission(commission=comm)
    initial_portfolio_value = cerebro.broker.getvalue()
    results = cerebro.run()
    years = relativedelta(datetime.datetime.strptime(end, '%Y-%m-%d'), datetime.datetime.strptime(start, '%Y-%m-%d')).years
    annual_perc_ret = (((cerebro.broker.getvalue() - initial_portfolio_value) / initial_portfolio_value) * 100) / years
    print_backtest_analysis(initial_portfolio_value, cerebro.broker.getvalue(), years, results, annual_perc_ret)

    if plotting: cerebro.plot()

    return cerebro.broker.getvalue()

def print_backtest_analysis(init_val, final_val, years, results, annual_ret):
    print('Backtesting results:\n--------------------')
    print(f'Final Portfolio Value: ${final_val:,.2f}')
    print(f'Total Profit: ${final_val - init_val:,.2f}')
    print(f'Avg. Percent Return P.A: {(((final_val - init_val) / init_val) * 100) / years:,.2f}%') 
    print(f'Avg. Profit P.A: ${(final_val - init_val) / years:,.2f}')
    print(f'Avg. Sharpe Ratio: {results[0].analyzers.mysharpe.get_analysis()["sharperatio"]:.2f}')
    print(f'Avg. SQN: {results[0].analyzers.sqn.get_analysis()["sqn"]:.2f}')
    print(f'Avg. VWR: {results[0].analyzers.vwr.get_analysis()["vwr"]:.2f}')
    strategy_rating = calculate_strategy_rating(results, annual_ret)
    print(f'Strategy Rating: {strategy_rating} stars\n--------------------')
    

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
# def test():
#     # optimise(strategies.ETHScalping, {
#     #         "buy_threshold": np.linspace(500,600,3),
#     #         "sell_threshold": np.linspace(900,1000,3),
#     #         "sma_period": range(10,20)
#     #     }, ['ETHUSD'], '2015-06-01', '2023-02-10', TimeFrame.Day, 10000, 0.0, False)

#     strat_params = {
#         'frequency': 'monthly',
#         'weights': {
#             'MSFT': 0.3,
#             'AAPL': 0.3,
#         },
#     }

#     # params = {
#     #     'period': range(14,65),
#     # }

#     # optimise(strategies.SimpleSMA, params, ['ETHUSD'], '2015-01-01', '2023-01-01', TimeFrame.Day, 10000, 0.0, False)
#     # optimise(strategies.Rebalance, params, ['MSFT', 'AAPL'], '2020-01-01', '2023-01-01', TimeFrame.Day, 10000, 0.0, False)
# # optimise(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
#     backtest(strategies.Rebalance, strat_params, ['MSFT','AAPL'], user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
# # backtest(strategies.ETHScalping, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, 0.0, False)