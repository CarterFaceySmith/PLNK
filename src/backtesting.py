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

user_start = input("Enter a start date for backtesting (format: yyyy-mm-dd): ")
user_end = input("Enter an end date for backtesting (format: yyyy-mm-dd): ")

if user_end < user_start:
    raise ValueError("End date must be after the start date")

'''
    Backtest function intakes:
        - The strategy to test, an instance of a defined backtrader.strategy object
        - A dictionary of parameters to utilise in the strategy
        - A list of tickers whose data to retrieve for analysis
        - A start and end date as a string of form 'yyyy-mm-dd'
        - A TimeFrame interval, either day, month or year to retrieve the tickers' bars
        - The initial capital amount to test on as an integer, defaulting to 100,000
'''
def backtest(strategy, strat_params, symbols, start, end, timeframe=TimeFrame.Day, cash=100000):
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(strategy, strat_params)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

    if len(symbols) <= 0 or len(strat_params) <= 0:
        raise ValueError("Invalid symbols list and/or parameters were fed into the backtest function")

    elif type(symbols) == str:
        if(symbols in config.crypto):
            try:
                alpaca_data = rest_api.get_crypto_bars(symbols, timeframe, start, end).df
            except:
                raise(BaseException(f"Error retrieving {symbols} bars from Alpaca API"))
        else:
            try:
                alpaca_data = rest_api.get_bars(symbols, timeframe, start, end).df
            except:
                raise(BaseException(f"Error retrieving {symbols} bars from Alpaca API"))
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbols)
        cerebro.adddata(data)
        print(f'Added {symbols} data to cerebro instance\n')
        print(f"{alpaca_data.head(3)}\n")


    elif type(symbols) == list or type(symbols) == set:
        for symbol in symbols:
            if(symbol in config.crypto):
                try:
                    alpaca_data = rest_api.get_crypto_bars(symbol, timeframe, start, end).df
                except:
                    raise(BaseException(f"Error retrieving {symbol} bars from Alpaca API"))
            else:
                try:
                    alpaca_data = rest_api.get_bars(symbol, timeframe, start, end).df
                except:
                    raise(BaseException(f"Error retrieving {symbol} bars from Alpaca API"))
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)
            print(f'Added {symbol} data to cerebro instance\n')
            print(f"{alpaca_data.head(3)}\n")

    initial_portfolio_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_portfolio_value:,}')
    results = cerebro.run(maxcpus=1)
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Final Portfolio Value: {final_portfolio_value:,.2f} ---> Return: {((final_portfolio_value/initial_portfolio_value - 1)*100):,.2f}%')

    strat = results[0]
    sharpe_rat = strat.analyzers.mysharpe.get_analysis()['sharperatio']
    print(f'Sharpe Ratio: {sharpe_rat:.2f}')
    # cerebro.plot(iplot= False)

class Rebalance(bt.Strategy):
    params = (
        ('weights',{}),
        ('frequency',''),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                #For each thing in fed in params, there must be a matching objects in self.params which is then set to the fed-in corresponding val
                setattr(self.params, name, val)
        self.month_last_rebalanced = -1 
        self.year_last_rebalanced = -1
        self.day_last_rebalanced = -1

    def next(self):
        match self.params.frequency:
            case 'yearly':
                if (self.datetime.date().year == self.year_last_rebalanced):
                    return
                self.year_last_rebalanced = self.datetime.date().year
            case 'monthly':
                if (self.datetime.date().year == self.year_last_rebalanced) and (self.datetime.date().month == self.month_last_rebalanced):
                    return
                self.year_last_rebalanced = self.datetime.date().year
                self.month_last_rebalanced = self.datetime.date().month

        for i,d in enumerate(self.datas):
                symbol = d._name
                self.order_target_percent(d, target=self.params.weights[symbol])

# weights = {"MSFT":0.2,"BTCUSD":0.2,"GOOG":0.2,"ETHUSD":0.3}
# tickers = list(weights.keys())
# user_start = "2015-01-01"
# user_end = "2023-02-01"
strat_params = {'weights':weights, 'frequency':'monthly'}

backtest(Rebalance, strat_params, tickers, user_start, user_end, TimeFrame.Day, 100000)