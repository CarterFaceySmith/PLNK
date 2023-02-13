import backtrader as bt
from alpaca.data.timeframe import TimeFrame
import config

rest_api = config.rest_api

tickers = input("Enter the stock tickers separated by commas: ").split(',')
allocation_input = input("Enter the target allocations for each stock separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
target_allocations = [float(x) for x in allocation_input]

if sum(target_allocations) > 1 or sum(target_allocations) < 0:
    raise ValueError("The sum of your allocations must be between 0 and 1")

weights = dict(zip(tickers, target_allocations))

def backtest(strategy, strat_params, symbols, start, end, timeframe=TimeFrame.Day, cash=10000):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

    if len(symbols) <= 0 or len(strat_params) <= 0:
        raise ValueError("Invalid symbols list and/or parameters were fed into the backtest function")

    elif type(symbols) == str:
        if(symbols in config.crypto):
            alpaca_data = rest_api.get_crypto_bars(symbols, timeframe, start, end).df
        else:
            alpaca_data = rest_api.get_bars(symbols, timeframe, start, end).df
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbols)
        cerebro.adddata(data)
        print(f'Added {symbols} data to cerebro instance\n')

    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            if(symbol in config.crypto):
                alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
            else:
                alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)
            print(f'Added {symbol} data to cerebro instance\n')


    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value} ---> Return: {(final_portfolio_value/initial_portfolio_value - 1)*100}%')

    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.mysharpe.get_analysis()['sharperatio'])
    # cerebro.plot(iplot= False)

class Rebalance(bt.Strategy):

   def __init__(self, weights):
       self.weights = weights
       self.year_last_rebalanced = -1 

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

backtest(Rebalance, weights, tickers, '2020-01-01', '2023-02-01', TimeFrame.Day, 100000)