import yfinance as yf
import backtrader.feeds as btfeeds
import backtrader as bt
from datetime import datetime
import numpy as np

class RebalanceStrategy(bt.Strategy):
    params = (('rebalance_days', 90), ('threshold', 0.05))

    def __init__(self):
        self.counter = 0
        self.values = np.zeros(len(self.datas))

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        self.counter += 1

        # Log the closing prices of the series from the reference
        if self.counter % 30 == 0:  # Log every 30 days
            for i, d in enumerate(self.datas):
                self.log('Close, %s: %.2f' % (d._name, d.close[0]))

        # Rebalance if the portfolio deviates from the target allocation by a certain threshold
        if self.counter % self.params.rebalance_days == 0 or self.check_threshold():
            self.rebalance_portfolio()

    def check_threshold(self):
        total_value = self.broker.getvalue()
        target_value = total_value / len(self.datas)

        for i, d in enumerate(self.datas):
            current_value = self.broker.getposition(d).size * d.close[0]
            if abs(current_value - target_value) / target_value > self.params.threshold:
                return True

        return False

    def rebalance_portfolio(self):
        # Rebalance based on volatility
        total_value = self.broker.getvalue()
        volatilities = np.array([np.std(d.close.get(size=self.params.rebalance_days)) for d in self.datas])

        # Add a small constant to avoid division by zero
        volatilities += 1e-10

        weights = 1 / volatilities
        weights = weights / np.sum(weights)

        for i, d in enumerate(self.datas):
            target_value = total_value * weights[i]
            current_value = self.broker.getposition(d).size * d.close[0]
            difference = target_value - current_value

            if difference > 0:
                self.buy(data=d, size=difference / d.close[0])
                self.log('BUY CREATE, %s: %.2f' % (d._name, d.close[0]))
            elif difference < 0:
                self.sell(data=d, size=-difference / d.close[0])
                self.log('SELL CREATE, %s: %.2f' % (d._name, d.close[0]))

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(RebalanceStrategy)

    # Add the stocks
    symbols = ['MSFT', 'BTC-USD']
    for symbol in symbols:
        data_df = yf.download(symbol, start='2022-01-01', end='2023-08-01')
        data = btfeeds.PandasData(dataname=data_df)
        cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    # Set the commission - $2 per trade
    cerebro.broker.setcommission(commission=2.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
