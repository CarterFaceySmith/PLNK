import asyncio
import datetime
from src import backtesting, strategies, config
from alpaca.data.timeframe import TimeFrame
import numpy as np
import backtrader as bt
import itertools

# def generate_weight_combinations(base_weights):
#     # Generate weight combinations in 5 percent increments
#     weight_combinations = []
#     tickers = list(base_weights.keys())
#     num_tickers = len(tickers)

#     # Iterate through all combinations
#     for i in range(num_tickers + 1):
#         for combo in itertools.combinations(tickers, i):
#             remaining_weight = 1.0
#             new_weights = base_weights.copy()

#             for ticker in combo:
#                 increment = 0.01
#                 new_weights[ticker] = increment
#                 remaining_weight -= increment

#             # Distribute the remaining weight proportionally
#             if remaining_weight > 0:
#                 for ticker in tickers:
#                     new_weights[ticker] += remaining_weight / num_tickers

#             weight_combinations.append(new_weights)

#     return weight_combinations

# def test():
#     strat_params = {
#         'frequency': 'monthly',
#         'weights': {
#             'VOO': 0.4,
#             'VOOG': 0.2,
#             'BTC-USD': 0.2,
#             'ETH-USD': 0.15,
#         },
#     }

#     user_start = "2010-01-01"
#     user_end = "2023-09-01"
    
#     # Generate weight combinations
#     base_weights = strat_params['weights']
#     weight_combinations = generate_weight_combinations(base_weights)
    
#     # Initialize variables to keep track of the optimal combination and return
#     optimal_weights = None
#     max_total_return = np.finfo(np.float64).min  # Initialize with a very small value
    
#     # Iterate through weight combinations and evaluate using backtesting
#     for weights in weight_combinations:
#         strat_params['weights'] = weights
#         print(f'\tTesting combo:\t{weights}\n')
#         total_return = backtesting.backtest(strategies.Rebalance, strat_params, list(weights.keys()), user_start, user_end, TimeFrame.Day, 50000, 0.0, False)
        
#         # Update optimal combination if needed
#         if total_return is not None and total_return > max_total_return and len(weights) > 1:
#             max_total_return = total_return
#             optimal_weights = weights
    
#     # Save the most optimal combination based on total return
#     if optimal_weights is not None:
#         print("Optimal Weights:", optimal_weights)
#         print("Total Return for Optimal Weights:", max_total_return)
#     else:
#         print("No valid total return found for any weight combination.")

async def test():
    strat_params = {
        'frequency': 'monthly',
        'weights': {
            # 'VAS.AX': 0.1,
            # 'VGS.AX': 0.3,
            # 'VGB.AX': 0.1,
            'VOO': 0.33,
            'VOOG': 0.1,
            'IBM': 0.05,
            'BTC-USD': 0.33,
            'ETH-USD': 0.17,
            # 'SPY': 0.5,
            # 'QQQ': 0.5,
        },
    }

    user_start = "2017-11-09"
    user_end = datetime.datetime.now().strftime("%Y-%m-%d")

    backtesting.backtest(strategies.Rebalance, strat_params, list(strat_params['weights'].keys()), user_start, user_end, TimeFrame.Day, 50000, 0.0)
    # backtesting.optimise(strategies.Rebalance, strat_params, list(strat_params['weights'].keys()), user_start, user_end, TimeFrame.Day, 50000)
    # backtesting.backtest(strategies.ETHScalping, params, ['ETHUSD'], user_start, user_end, TimeFrame.Day, 100000, 0.0, False)
    exit()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test())