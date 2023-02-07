import alpaca_trade_api as tradeapi
from alpaca.data.timeframe import TimeFrame
import backtrader as bt
import config

# Alpaca API key
API_KEY = config.API_KEY
API_SECRET = config.SECRET_KEY

# Define the strategy
class ScalpingStrategy(bt.Strategy):
    params = (
        ("buy_threshold", 800),
        ("sell_threshold", 900),
        ("sma_period", 50)
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )

    def next(self):
        if not self.position:
            if self.data.close[0] < self.params.buy_threshold:
                self.buy(price=self.data.close[0])
        else:
            if self.data.close[0] > self.params.sell_threshold:
                self.sell(price=self.data.close[0])

# Backtesting
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ScalpingStrategy)

    api = tradeapi.REST(API_KEY, API_SECRET, 'https://paper-api.alpaca.markets')

    data = api.get_crypto_bars("ETHUSD", TimeFrame.Day, start='2020-01-01', end='2020-01-01')
    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)
    cerebro.run()
    cerebro.plot()
