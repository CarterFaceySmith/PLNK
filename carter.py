import asyncio
from src import config, rebalance, backtesting, testing
from alpaca.trading.client import TradingClient

portfolio = {'VOO': 0.4, 'VOOG': 0.15, 'BTC-USD': 0.2, 'ETH-USD': 0.2}

async def main():
    client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=False)
    await config.send_message(config.chat_id, "REBALANCING:\n\n")
    rebalance.perform_rebalance(t_client=client, desired_allocations=portfolio)
    await config.send_update_msg()
    await config.send_message(config.chat_id, "\n\nREBALANCE COMPLETE.")
    exit()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())