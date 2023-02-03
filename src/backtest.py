import backtrader as bt
import matplotlib as plt
from alpaca_trade_api.rest import TimeFrame

plt.rcParams['figure.dpi'] = 150

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

    # initialize backtrader broker
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)

    # add strategy
    cerebro.addstrategy(strategy)

    # add analytics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    # historical data request
    if type(symbols) == str:
        symbol = symbols
        alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)
    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)


    # run
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value} ---> Return: {(final_portfolio_value/initial_portfolio_value - 1)*100}%')

    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.mysharpe.get_analysis()['sharperatio'])
    cerebro.plot(iplot= False)


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

# How to use  
# symbols = ["BTCUSD", "ETHUSD", "LTCUSD"]
# backtest(CryptoRebalance, symbols, '2020-01-01', '2022-11-01', TimeFrame.Day, 100000)