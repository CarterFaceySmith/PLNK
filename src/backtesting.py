import backtrader as bt
from alpaca.data.timeframe import TimeFrame
import config, strategies, datetime
from dateutil.relativedelta import relativedelta

rest_api = config.rest_api

# tickers = input("Enter the stock tickers separated by commas: ").split(',')
# allocation_input = input("Enter the target allocations for each stock separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
# target_allocations = [float(x) for x in allocation_input]

# if sum(target_allocations) > 1 or sum(target_allocations) < 0:
#     raise ValueError("The sum of your allocations must be between 0 and 1")

# weights = dict(zip(tickers, target_allocations))

# user_start = input("Enter a start date for backtesting (format: yyyy-mm-dd): ")
# user_end = input("Enter an end date for backtesting (format: yyyy-mm-dd): ")

# if user_end < user_start:
#     raise ValueError("End date must be after the start date")

'''
    Backtest function intakes:
        - The strategy to test, an instance of a defined backtrader.strategy object
        - A list of tickers whose data to retrieve for analysis
        - A start and end date as a string of form 'yyyy-mm-dd'
        - A dictionary of parameters to utilise in the strategy
        - A TimeFrame interval, either day, month or year to retrieve the tickers' bars
        - The initial capital amount to test on as an integer, defaulting to 100,000
        - A boolean switch for if you want to display a chart of results upon completion
'''
def backtest(strategy, strat_params=None, symbols=list, start="2016-06-01", end="2023-02-01", timeframe=TimeFrame.Day, cash=100000, plot=bool):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    
    for symbol in symbols:
        alpaca_data = config.get_historic_data(symbol, rest_api, timeframe, start, end)
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)
        print(f'Added {symbol} data to cerebro instance\n')
        print(f"{alpaca_data.head(3)}\n")

    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value:,}')
    results = cerebro.run(maxcpus=1)
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value:,.2f} ---> Return: {((final_portfolio_value/initial_portfolio_value - 1)*100):,.2f}%')
    difference_in_years = relativedelta(datetime.datetime.strptime(user_end, "%Y-%m-%d"), datetime.datetime.strptime(user_start, "%Y-%m-%d")).years
    print(f'Average Annualised Return: {(((final_portfolio_value/initial_portfolio_value - 1)*100)/difference_in_years):,.2f}%')

    strat = results[0]
    sharpe_rat = strat.analyzers.mysharpe.get_analysis()['sharperatio']
    print(f'Sharpe Ratio: {sharpe_rat:.2f}')
    if plot:
        cerebro.plot()

weights = {"ETHUSD":1.0}
tickers = list(weights.keys())
user_start = "2016-06-01"
user_end = "2023-02-01"

# strat_params = {'weights':weights, 'frequency':'monthly'}
# backtest(strategies.Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000, False)

# backtest(strategies.ETHScalping, None, tickers, user_start, user_end, TimeFrame.Day, 100000, False)
