import backtrader as bt
import matplotlib as plt
from alpaca_trade_api.rest import TimeFrame

""" 
Baseline functionality:
- The backtest function intakes a strategy (instance of bt.Strategy)
- Strategies can be defined and added/deleted from a dict of bt.Strategy classes
- Each strategy is defined as a class and takes in the default bt.Strategy as its only argument
- 
"""

# Settings
plt.rcParams['figure.dpi'] = 150
crypto_symbols = {"BTCUSD", "ETHUSD", "LTCUSD"}
strategies = {}

def backtest(strategy, rest_api, symbols, start, end, timeframe=TimeFrame, cash=10000):
    """params:
        strategy: the strategy you wish to backtest, an instance of backtrader.Strategy
        symbols: the symbol (str) or list of symbols List[str] you wish to backtest on
        start: start date of backtest in format 'YYYY-MM-DD'
        end: end date of backtest in format: 'YYYY-MM-DD'
        timeframe: the timeframe the strategy trades on (size of bars) -
                    1 min: TimeFrame.Minute, 1 day: TimeFrame.Day, 5 min: TimeFrame(5, TimeFrameUnit.Minute)
        cash: the starting cash of backtest
    """

    # Initialise backtrader
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)

    # Add strategy
    cerebro.addstrategy(strategy)

    # Add analytics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

    # Request historical ticker data
    if type(symbols) == str:
        symbol = symbols
        if symbol in crypto_symbols:
            alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)
        elif symbol not in crypto_symbols:
            alpaca_data = rest_api.get_latest_bars(symbol, timeframe, start, end).df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)
        else:
            SyntaxError('Invalid symbol')
        
    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            if symbol in crypto_symbols:
                alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
                data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
                cerebro.adddata(data)
            elif symbol not in crypto_symbols:
                alpaca_data = rest_api.get_latest_bars(symbol, timeframe, start, end).df
                data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
                cerebro.adddata(data)
            else:
                SyntaxError('Invalid symbol')


    # Run backtest
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value} ---> Return: {(final_portfolio_value/initial_portfolio_value - 1)*100}%')

    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.mysharpe.get_analysis()['sharperatio'])
    cerebro.plot(iplot= False)

# Print all stored strategies to console
def print_strategies():
    for strat in strategies:
        print("Strategy {}:\t{}\n".format(strategies.index(strat),strat))

# Search for and delete strategy from storage
def delete_strategy(strategy_name):
    if strategy_name in strategies:
        print("Match found.\n")
        strategies.pop(strategy_name)
        print("Strategy deleted successfully\n")

# Strategies
class CryptoRebalance(bt.Strategy):

   def __init__(self):
       # the last year we rebalanced (initialized to -1)
       self.year_last_rebalanced = -1 
       self.weights = { "BTCUSD" : 0.45 , "ETHUSD" : 0.35,  "LTCUSD" : 0.15 }

   def next(self):
       # if we’ve already rebalanced this year
       if self.datetime.date().year == self.year_last_rebalanced:
           return
       # update year last balanced
       self.year_last_rebalanced = self.datetime.date().year
       # enumerate through each security
       for i,d in enumerate(self.datas):
           # rebalance portfolio with desired target percents
           symbol = d._name
           self.order_target_percent(d, target=self.weights[symbol])

"""
How to call:  
    symbols = ["BTCUSD", "ETHUSD", "LTCUSD"]
    backtest(CryptoRebalance, restAPI, symbols, '2020-01-01', '2022-11-01', TimeFrame.Day, 100000)
"""