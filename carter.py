import asyncio
from src import config, rebalance, backtesting, testing
from alpaca.trading.client import TradingClient

# portfolio = {'VOO': 0.4, 'VOOG': 0.1, 'IBM': 0.05, 'BTCUSD': 0.2, 'ETHUSD': 0.2}
portfolio = {'VOO': 0.33, 'VOOG': 0.1, 'IBM': 0.05, 'BTCUSD': 0.33, 'ETHUSD': 0.17,}


async def main():
    # input("Press Enter to confirm live rebalance...")
    await rebalance.perform_live_rebalance(trading_client=config.live_client, desired_allocations=portfolio)
    # await config.send_message("Test message - scheduled job performed by daemon.")
    exit()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())