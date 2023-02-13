import backtrader as bt

class Rebalance(bt.Strategy):
    params = (
        ('weights',{}),
        ('frequency',''),
        ('maperiod', 15)
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

    def next(self):
        if not self.position:
            if self.data.close[0] < self.params.buy_threshold:
                self.buy(price=self.data.close[0])
        else:
            if self.data.close[0] > self.params.sell_threshold:
                self.sell(price=self.data.close[0])

strategy_dict = {'Rebalance': Rebalance, 'Ethereum Scalping': ETHScalping}
strategy_list = list(strategy_dict.keys())

def list_strats():
    i = 1
    for name in strategy_dict:
        print(f'{i}: {name}')
        i += 1
    print("\n")

def select_strat():
    list_strats()
    selection = input("Select strategy: ")
    selection_name = strategy_list[int(selection)-1]
    return strategy_dict[selection_name]
