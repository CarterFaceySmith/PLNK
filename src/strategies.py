import backtrader as bt
import re, numpy

# NOTE: You cannot iterate over an instance of self.params in a strategy
# NOTE: You need to convert to an integer or float if you want to use the value in pre-set params, this should be done in the strategy init, otherwise a string version is fed in from input() at line 18 or 38 of backtesting.py and the code will give a type error

# Strategies
class Rebalance(bt.Strategy):
    params = (
        ('frequency',''),
        ('weights',{}),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                setattr(self.params, name, val)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def start(self):
        self.month_last_rebalanced = -1
        self.year_last_rebalanced = -1
        self.start_cash = self.broker.getvalue()

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

        for index, datafeed in enumerate(self.datas):
            # NOTE: i = count, d = datafeed instance in self.datas
            symbol = datafeed._name
            self.order_target_percent(datafeed, target=self.params.weights[symbol])
            # NOTE: self.order_target_percent() can take a string value or datafeed instance as the first argument

    def stop(self):
        self.log(f'Weights: {self.params.weights}\tFrequency: {self.params.frequency}\tProfit: {self.broker.getvalue() - self.start_cash:,.2f}', doprint=True)

class RebalanceAndAdd(bt.Strategy):
    params = dict(
        monthly_cash=1000.0,  # amount of cash to buy every month
    )

    def start(self):
        # Activate the fund mode and set the default value at 100
        self.broker.set_fundmode(fundmode=True, fundstartval=100.00)

        self.cash_start = self.broker.get_cash()
        self.val_start = 100.0

        # Add a timer which will be called on the 1st trading day of the month
        self.add_timer(
            bt.timer.SESSION_END,  # when it will be called
            monthdays=[1],  # called on the 1st day of the month
            monthcarry=True,  # called on the 2nd day if the 1st is holiday
        )

    def notify_timer(self, timer, when, *args, **kwargs):
        # Add the influx of monthly cash to the broker
        self.broker.add_cash(self.p.monthly_cash)

        # buy available cash
        target_value = self.broker.get_value() + self.p.monthly_cash
        self.order_target_value(target=target_value)

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() - self.cash_start) - 1.0
        self.froi = self.broker.get_fundvalue() - self.val_start
        print('ROI:        {:.2f}%'.format(self.roi))
        print('Fund Value: {:.2f}%'.format(self.froi))

class ETHScalping(bt.Strategy):
    params = (
        ("buy_threshold", 800),
        ("sell_threshold", 900),
        ("sma_period", 50),
        ("printlog", False),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                if isinstance(val, numpy.linspace):
                    setattr(self.params, name, val)
                else:
                    setattr(self.params, name, int(val))

        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        self.start_cash = self.broker.getvalue()
    
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if not self.position:
            if self.data.close[0] < self.params.buy_threshold:
                self.buy(price=self.data.close[0])
        else:
            if self.data.close[0] > self.params.sell_threshold:
                self.sell(price=self.data.close[0])

    def stop(self):
        self.log(f'Buy Threshold: {self.params.buy_threshold}\tSell Threshold: {self.params.sell_threshold}\tPeriod: {self.params.sma_period}\tProfit: {self.broker.getvalue() - self.start_cash:,.2f}', doprint=True)

class SimpleSMA(bt.Strategy):
    params = (
        ('period', 21),
        ('printlog', False),
        )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items(): 
                setattr(self.params, name, int(val))
        self.start_cash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.period)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

    def stop(self):
        self.log(f'Period: {self.params.period}\tProfit: {self.broker.getvalue() - self.start_cash:,.2f}', doprint=True)

# Utilities
strategy_dict = {'Rebalance': Rebalance, 'RebalanceAndAdd': RebalanceAndAdd, 'Ethereum Scalping': ETHScalping, 'Simple SMA': SimpleSMA}
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