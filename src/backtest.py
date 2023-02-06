import backtrader as bt
import matplotlib as plt
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import config
from datetime import datetime

""" 
Baseline functionality:
- We are using the backtrader framework to run testing
- The backtest function intakes a strategy (instance of bt.Strategy)
- Strategies can be defined and added/deleted from a dict of bt.Strategy classes
- Each strategy is defined as a class and takes in the default bt.Strategy as its only argument
- 
"""

# Settings
plt.rcParams['figure.dpi'] = 150
crypto_symbols = ['BTC/USD', 'ETH/USD']
strategies = {}
cerebro = bt.Cerebro(stdstats=True)
crypto_data_client = CryptoHistoricalDataClient()
stock_data_client = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)

def backtest(strategy, symbols, start, timeframe=TimeFrame, cash=10000):
    """params:
        strategy: the strategy you wish to backtest, an instance of backtrader.Strategy
        symbols: the symbol (str) or list of symbols List[str] you wish to backtest on
        start: start date of backtest in format 'YYYY-MM-DD'
        end: end date of backtest in format: 'YYYY-MM-DD'
        timeframe: the timeframe the strategy trades on (size of bars) -
                    1 min: TimeFrame.Minute, 1 day: TimeFrame.Day, 5 min: TimeFrame(5, TimeFrameUnit.Minute)
        cash: the starting cash of backtest
    """

    # Initialise backtrader Cerebro instance
    cerebro.broker.setcash(cash)

    # Add strategy
    cerebro.addstrategy(strategy)

    # Add analytics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

    # Request historical ticker data
    if type(symbols) == str: req_hist_data(symbols, timeframe, start)
        
    else: 
        for symbol in symbols:
            req_hist_data(symbol, timeframe, start)
            


    # Run backtest
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value} ---> Return: {(final_portfolio_value/initial_portfolio_value - 1)*100}%')

    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.mysharpe.get_analysis()['sharperatio'])
    # cerebro.plot(iplot= False)

def req_hist_data(symbol, timeframe, start):
    # CRYPTO
    if symbol in crypto_symbols:
            request = CryptoBarsRequest(symbol_or_symbols=symbol, timeframe=timeframe, start=datetime.strptime(start, '%Y-%m-%d'))
            data = crypto_data_client.get_crypto_bars(request).df

            # Convert to a backtrader feed
            data = bt.feeds.PandasData(dataname=data, name=symbol)
            cerebro.adddata(data)
    # STOCK
    elif symbol not in crypto_symbols:
        request = StockBarsRequest(symbol_or_symbols=symbol, timeframe=timeframe, start=datetime.strptime(start, '%Y-%m-%d'))
        data = stock_data_client.get_stock_bars(request).df

        # Convert to a backtrader feed
        data = bt.feeds.PandasData(dataname=data, name=symbol)
        cerebro.adddata(data)
    else:
            SyntaxError('Invalid symbol')

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

def log(self, txt, dt=None, doprint=False):
        ''' Logging function for each strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

# Strategies
class Rebalance(bt.Strategy):
    params = (
        ('weights', {'BTC/USD':  0.45}),
    )

    def __init__(self):
       # the last year we rebalanced (initialized to -1)
       self.year_last_rebalanced = -1 
       self.weights = self.params.weights

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

symbols = ['BTC/USD']
# TODO: Replance the symbols with a direct call from the strategy
backtest(Rebalance, symbols, '2020-01-01', TimeFrame.Day, 100000)