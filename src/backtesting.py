import backtrader as bt
from alpaca.data.timeframe import TimeFrame
import alpaca_trade_api as tradeapi
import config

rest_api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto = ['BTCUSD', 'ETHUSD']

tickers = input("Enter the stock tickers separated by commas: ").split(',')
allocation_input = input("Enter the target allocations for each stock separated by commas (e.g. 0.3,0.2,0.5): ").split(',')
target_allocations = [float(x) for x in allocation_input]

# Ensure that the sum of target allocations is 1
if sum(target_allocations) > 1 or sum(target_allocations) < 0:
    raise ValueError("The sum of your allocations must be between 0 and 1")

portfolio = dict(zip(tickers, target_allocations))

def backtest(strategy, strat_params, symbols, start, end, timeframe=TimeFrame.Day, cash=10000):
    # initialize backtrader broker
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

    if type(symbols) == str:
        if(symbols in crypto):
            alpaca_data = rest_api.get_crypto_bars(symbols, timeframe, start, end).df
        else:
            alpaca_data = rest_api.get_bars(symbols, timeframe, start, end).df
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbols)
        cerebro.adddata(data)

    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            if(symbol in crypto):
                alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
            else:
                alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)

    # Run testing
    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value}')
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value} ---> Return: {(final_portfolio_value/initial_portfolio_value - 1)*100}%')

    strat = results[0]
    print('Sharpe Ratio:', strat.analyzers.mysharpe.get_analysis()['sharperatio'])
    # cerebro.plot(iplot= False)

class Rebalance(bt.Strategy):
   
   params = (
       ('weights',{})
   )

   def __init__(self, params=None):
       if params != None:
            for name, val in params.items():
                setattr(self.params, name, val) # Could change to directly write as per below line 65?
       self.year_last_rebalanced = -1 
    #    self.weights = { "BTCUSD" : 0.15, "MSFT" : 0.2, "ETHUSD" : 0.05, "VOO" : 0.4, "VOOG" : 0.2}

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

backtest(Rebalance, portfolio, tickers, '2022-01-01', '2023-02-01', TimeFrame.Day, 100000)