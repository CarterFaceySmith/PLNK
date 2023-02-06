import alpaca_trade_api as tradeapi
import pandas as pd
import config

# Authenticate to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')

# Define the target allocation for each stock in the portfolio
target_allocation = {
    'AAPL': 0.3,
    'GOOG': 0.3,
    'TSLA': 0.1,
    'ASTS': 0.1,
    'MSFT': 0.1,
    'VOO': 0.1,
    'VOOG': 0.1
}

# Get the current portfolio data
api.close_all_positions()
portfolio = api.list_positions()
api.get_bars

# Calculate the current total value of the portfolio
portfolio_value = sum(float(position.market_value) for position in portfolio)

# Create a dataframe from the portfolio data
df = pd.DataFrame([(position.symbol, position.market_value) for position in portfolio], columns=['symbol', 'market_value'])

# Calculate the target value for each stock based on the target allocation
df['target_value'] = df['symbol'].apply(lambda x: target_allocation[x] * portfolio_value)

# Calculate the difference between the current value and the target value
df['difference'] = df['target_value'] - df['market_value']

# Rebalance the portfolio by selling stocks that are above target and buying stocks that are below target
for index, row in df.iterrows():
    symbol = row['symbol']
    difference = row['difference']
    
    if difference > 0:
        # Buy more of this stock
        qty = int(difference / api.get_last_trade(symbol).price)
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='limit',
            time_in_force='gtc',
            limit_price=api.get_last_trade(symbol).price
        )
    elif difference < 0:
        # Sell some of this stock
        qty = int(-difference / api.get_last_trade(symbol).price)
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='limit',
            time_in_force='gtc',
            limit_price=api.get_last_trade(symbol).price
        )
