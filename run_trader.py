#!/usr/bin/env python3
import sys

from autotrader.config import load_settings
from autotrader.broker.alpaca import AlpacaBroker
from autotrader.engine.live_engine import LiveEngine


def main() -> int:
    settings = load_settings()

    broker = AlpacaBroker(
        api_key=settings.alpaca_api_key,
        api_secret=settings.alpaca_api_secret,
        base_url=settings.alpaca_base_url,
        data_base_url=settings.alpaca_data_base_url,
    )

    engine = LiveEngine(
        broker=broker,
        symbol=settings.symbol,
        timeframe=settings.time_frame,
        rsi_period=settings.rsi_period,
        buy_threshold=settings.rsi_buy_threshold,
        sell_threshold=settings.rsi_sell_threshold,
        position_size_usd=settings.position_size_usd,
        poll_seconds=settings.poll_seconds,
    )

    engine.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
