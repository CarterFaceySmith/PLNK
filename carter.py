import asyncio
from src import config, rebalance, backtesting, testing
from alpaca.trading.client import TradingClient

portfolio = {'VOO': 0.4, 'VOOG': 0.1, 'IBM': 0.05, 'BTC-USD': 0.2, 'ETH-USD': 0.2}

async def main():
    client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=False)
    await config.send_message("---------------------\nRebalancing:\n")
    rebalance.perform_live_rebalance(t_client=client, desired_allocations=portfolio)
    await config.send_update_msg()
    await config.send_message("\n---------------------\nRebalancing complete.")
    exit()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())