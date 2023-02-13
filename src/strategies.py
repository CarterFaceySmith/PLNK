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
