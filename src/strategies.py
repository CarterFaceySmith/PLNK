import backtrader as bt
import re

# NOTE: You cannot iterate over an instance of self.params in a strategy

# Strategies
class Rebalance(bt.Strategy):
    params = (
        ('frequency',''),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                setattr(self.params, name, val)
        self.init_params = params
        self.month_last_rebalanced = -1 
        self.year_last_rebalanced = -1
        self.day_last_rebalanced = -1
        self.start_cash = self.broker.getvalue()

    def stop(self):
        profit = round(self.broker.getvalue() - self.start_cash,2)
        print(f'Profit: {profit:,.2f}\nPortfolio:')
        for item in self.init_params: 
            if re.match(r'[A-Z]{6}', item):
                print(f'\t{item}:\t{self.init_params[item]}')

            # if re.match(r'[A-Z]{6}', item): 
            #     print(f'\t{item}:\t{self.init_params[item]}')

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
            # NOTE: i = count, d = datafeed instance in self.datas
            if re.match(r'[A-Z]{6}', d._name):
                symbol = d._name
                allocation = self.params._get(symbol)
                self.order_target_percent(symbol, self.params._get(symbol))
            # NOTE: self.order_target_percent() can take a string value or datafeed instance as the first argument

class ETHScalping(bt.Strategy):
    params = (
        ("buy_threshold", 800),
        ("sell_threshold", 900),
        ("sma_period", 50)
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                setattr(self.params, name, val)
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        self.start_cash = self.broker.getvalue()

    def next(self):
        if not self.position:
            if self.data.close[0] < self.params.buy_threshold:
                self.buy(price=self.data.close[0])
        else:
            if self.data.close[0] > self.params.sell_threshold:
                self.sell(price=self.data.close[0])

    def stop(self):
        profit = round(self.broker.getvalue() - self.start_cash,2)
        print(f'Profit: {profit}\nSMA Period: {self.params.sma_period}\nBuy Threshold: {self.params.buy_threshold}\nSell Threshold: {self.params.sell_threshold}\n')

# Utilities
strategy_dict = {'Rebalance': Rebalance, 'Ethereum Scalping': ETHScalping}
strategy_list = list(strategy_dict.keys())

# Lists the available strategies
def list_strats():
    i = 1
    for name in strategy_dict:
        print(f'\t{i}: {name}')
        i += 1
    print()

# Lists the available strategies and returns the selected strategy object
def select_strat():
    list_strats()
    selection = input("Select strategy: ")
    selection_name = strategy_list[int(selection)-1]
    return strategy_dict[selection_name]
