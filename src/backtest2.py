import backtrader as bt
import matplotlib as plt
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import alpaca_trade_api as tradeapi
import config

rest_api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto = ['BTCUSD', 'ETHUSD']

def run_backtest(strategy, symbols, start, end, timeframe=TimeFrame.Day, cash=10000):
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
    cerebro.addstrategy(strategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')


    if type(symbols) == str:
        symbol = symbols
        if(symbol in crypto):
            alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
        else:
            alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df

        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
        cerebro.adddata(data)

    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            if(symbol in crypto):
                alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
            else:
                alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df
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


# Strategies
class Rebalance(bt.Strategy):

   def __init__(self):
       # the last year we rebalanced (initialized to -1)
       self.year_last_rebalanced = -1 
       self.weights = { "BTCUSD" : 0.15, "MSFT" : 0.15, "ETHUSD" : 0.05, "VOO" : 0.5, "VOOG" : 0.15}

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

portfolio = ["BTCUSD", "MSFT", "ETHUSD", "VOO", "VOOG"]
# TODO: Replance the symbols with a direct call from the strategy
run_backtest(Rebalance, portfolio, '2020-01-01', '2023-02-01', TimeFrame.Day, 100000)