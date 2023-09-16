import yfinance as yf
import backtrader.feeds as btfeeds
import backtrader as bt
from datetime import datetime
import numpy as np
import pandas as pd
import itertools
from src import config

class Rebalance(bt.Strategy):
    params = (
        ('weights', {
            'MSFT': 0.05,
            'AAPL': 0.05,
            'GOOG': 0.05,
            'VOO': 0.40,
            'VOOG': 0.15,
            'BTC-USD': 0.20,
            'ETH-USD': 0.10,
        }),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                setattr(self.params, name, val)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def start(self):
        self.month_last_rebalanced = -1
        self.year_last_rebalanced = -1
        self.start_cash = self.broker.getvalue()

    def next(self):
        if (self.datetime.date().year == self.year_last_rebalanced) and (self.datetime.date().month == self.month_last_rebalanced):
            return
        self.year_last_rebalanced = self.datetime.date().year
        self.month_last_rebalanced = self.datetime.date().month
        
        for i, d in enumerate(self.params.weights):
            # NOTE: i = count, d = datafeed instance in self.datas
            self.order_target_percent(d, target=self.params.weights[d])
            # NOTE: self.order_target_percent() can take a string value or datafeed instance as the first argument

if __name__ == '__main__':
    # cerebro = bt.Cerebro()

    # cerebro.addstrategy(Rebalance)

    # Add the stocks
    symbols = ['MSFT', 'AAPL', 'ETH-USD', 'GOOG', 'VOO', 'VOOG', 'BTC-USD']

    start_date = '2010-01-01'
    end_date = '2023-09-01'

    # Load the CSV data for each financial asset
    assets = ['VOO', 'VOOG', 'BTC-USD', 'ETH-USD']

    data = {}
    for asset in assets:
        data[asset] = pd.read_csv(f"{asset}_financial_data.csv", parse_dates=True)

    # Define the range of percentage allocations in 5% increments
    allocation_range = range(0, 101, 10)

    # Initialize variables to track the best combination
    best_allocation = None
    best_returns = -float('inf')

    # Define the initial portfolio value and monthly contribution
    initial_portfolio_value = 1000  # Replace with your desired initial investment
    monthly_contribution = 100  # Replace with your desired monthly contribution

    # Iterate through all possible combinations of allocations
    for allocation_combination in itertools.product(allocation_range, repeat=len(assets)):
        total_allocation = sum(allocation_combination)
        if total_allocation != 100:
            continue  # Skip combinations that don't add up to 100%

        portfolio_value = initial_portfolio_value
        portfolio_returns = []

        print(f'\tRunning allocation: {allocation_combination}')

        for year in range(2010, 2024):  # Adjust the range as needed
            for month in range(1, 13):
                # Calculate the current month's returns based on allocation
                month_returns = 0.0
                for i, asset in enumerate(assets):
                    allocation_percentage = allocation_combination[i] / 100
                    asset_data = data[asset]
                    returns = (asset_data['Adj Close'] / asset_data['Adj Close'].shift(1) - 1).fillna(0)
                    weighted_returns = allocation_percentage * returns
                    # Check if there are remaining funds to invest in this asset
                    if portfolio_value > 0:
                        month_returns += weighted_returns.mean()
                
                # Calculate the monthly portfolio value
                portfolio_value += monthly_contribution
                portfolio_value *= (1 + month_returns)
                portfolio_returns.append(portfolio_value)

       # Calculate the annualized returns
        final_portfolio_value = portfolio_returns[-1]
        years = len(portfolio_returns) / 12  # Calculate the number of years
        annualized_returns = (((final_portfolio_value / initial_portfolio_value) ** (1 / years)) - 1) * 100
        print(f'\tAnnualized returns: {annualized_returns:.4f}%')
        print(f'\tTotal gain: ${final_portfolio_value - initial_portfolio_value:,.4f}')
        print(f'\tYearly gain: ${(final_portfolio_value - initial_portfolio_value) / years:,.4f}\n')

        # Check if this combination yields the highest returns
        if annualized_returns > best_returns:
            best_returns = annualized_returns
            best_allocation = allocation_combination

    # Print the best combination of allocations and the corresponding annualized returns
    print("Best Allocation:", best_allocation)
    print("Best Annualized Returns:", best_returns)


    # for symbol in symbols:
        # cerebro.adddata(config.csv_to_df(symbol))

    # cerebro.broker.setcash(50000.0)
    # cerebro.broker.setcommission(commission=2.0)

    # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # cerebro.run()

    # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

