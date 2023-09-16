from src import backtesting, strategies, config
from alpaca.data.timeframe import TimeFrame
import numpy as np

def test():
    strat_params = {
        'frequency': 'monthly',
        'weights': {
            'MSFT': 0.075,
            'AAPL': 0.05,
            'GOOG': 0.075,
            'VOO': 0.4,
            'VOOG': 0.15,
            'BTC-USD': 0.225,
            'ETH-USD': 0.15,
        },
    }

    user_start = "2010-01-01"
    user_end = "2023-09-01"

    backtesting.backtest(strategies.Rebalance, strat_params, list(strat_params['weights'].keys()), user_start, user_end, TimeFrame.Day, 100000, 0.0, False)

    # backtesting.optimise(strategies.Rebalance, strat_params, list(strat_params['weights'].keys()), user_start, user_end, TimeFrame.Day, 100000)

    # backtesting.backtest(strategies.ETHScalping, params, ['ETHUSD'], user_start, user_end, TimeFrame.Day, 100000, 0.0, False)