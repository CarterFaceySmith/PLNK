import yfinance as yf
import backtrader.feeds as btfeeds
import backtrader as bt
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class Rebalance(bt.Strategy):
    params = (
        ('weights', {}),
    )

    def __init__(self, **kwargs):
        self.weights = kwargs.get('weights', {})

    def next(self):
        for data, weight in zip(self.datas, self.weights.values()):
            target_value = self.broker.getvalue() * weight
            current_value = self.broker.getposition(data).size * data.close[0]
            difference = target_value - current_value
            order_size = difference / data.close[0] - self.broker.getposition(data).size

            if order_size > 0:
                self.buy(data=data, size=order_size)
                self.log('BUY CREATE, %s: %.2f' % (data._name, data.close[0]))
            elif order_size < 0:
                self.sell(data=data, size=-order_size)
                self.log('SELL CREATE, %s: %.2f' % (data._name, data.close[0]))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

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
            order_size = difference / d.close[0] - self.broker.getposition(d).size

            if order_size > 0:
                self.buy(data=d, size=order_size)
                self.log('BUY CREATE, %s: %.2f' % (d._name, d.close[0]))
            elif order_size < 0:
                self.sell(data=d, size=-order_size)
                self.log('SELL CREATE, %s: %.2f' % (d._name, d.close[0]))

def optimize_allocation(dataframes, risk_free_rate=0.03):
    returns = []
    volatilities = []

    for df in dataframes:
        df['Log_Return'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
        df['Log_Return'].fillna(0, inplace=True)
        returns.append(df['Log_Return'].mean())
        volatilities.append(df['Log_Return'].std())

    returns = np.array(returns)
    volatilities = np.array(volatilities)

    # Calculate Sharpe ratio for different allocations
    sharpe_ratios = (returns - risk_free_rate) / volatilities

    # Find the allocation with the maximum Sharpe ratio
    max_sharpe_idx = np.argmax(sharpe_ratios)
    optimal_allocation = np.zeros(len(dataframes))
    optimal_allocation[max_sharpe_idx] = 1.0  # Allocate all to the asset with max Sharpe ratio

    return optimal_allocation

if __name__ == '__main__':
    symbols = ['ETH-USD', 'VOO', 'VOOG', 'BTC-USD']

    # Load and add financial data back from the CSV files
    dataframes = []

    for symbol in symbols:
        data_df = pd.read_csv(f"{symbol}_financial_data.csv", index_col='Date', parse_dates=True)
        dataframes.append(data_df)

    # Optimize the allocation
    optimized_weights = optimize_allocation(dataframes)

    # Print the optimized allocation
    print('Optimized Allocation:')
    for symbol, weight in zip(symbols, optimized_weights):
        print(f'{symbol}: {weight*100:.2f}%')

    # Normalize the weights to sum up to 1
    normalized_weights = optimized_weights / np.sum(optimized_weights)

    # Create a dictionary of ticker symbol to weight
    allocation = {symbol: weight for symbol, weight in zip(symbols, normalized_weights)}

    # Create and run the Backtrader strategy with the optimized allocation
    cerebro = bt.Cerebro()

    rebalance_params = dict(weights=allocation)
    cerebro.addstrategy(Rebalance, **rebalance_params)

    for symbol, data_df in zip(symbols, dataframes):
        data = bt.feeds.PandasData(dataname=data_df, name=symbol)
        cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    # Set the commission - $2 per trade
    cerebro.broker.setcommission(commission=2.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
