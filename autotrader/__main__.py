from __future__ import annotations

import argparse
import sys

from autotrader.config import load_config
from autotrader.broker import AlpacaBroker
from autotrader.engine import LiveEngine


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="RSI paper trading bot (Alpaca)")
    parser.add_argument("--symbols", type=str, default=None, help="Comma-separated symbols override (e.g., AAPL,MSFT)")
    parser.add_argument("--timeframe", type=str, default=None, help="Bar timeframe (e.g., 1Min, 5Min)")
    parser.add_argument("--period", type=int, default=None, help="RSI period (default from env or 14)")
    parser.add_argument("--buy", type=float, default=None, help="RSI buy threshold (default 30)")
    parser.add_argument("--sell", type=float, default=None, help="RSI sell threshold (default 70)")
    parser.add_argument("--qty", type=int, default=None, help="Order quantity per trade (default 1)")
    args = parser.parse_args(argv)

    cfg = load_config()

    if args.symbols:
        cfg.symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    if args.timeframe:
        cfg.timeframe = args.timeframe.strip()
    if args.period is not None:
        cfg.rsi_period = int(args.period)
    if args.buy is not None:
        cfg.rsi_buy_threshold = float(args.buy)
    if args.sell is not None:
        cfg.rsi_sell_threshold = float(args.sell)
    if args.qty is not None:
        cfg.order_qty = int(args.qty)

    broker = AlpacaBroker(cfg.alpaca_api_key, cfg.alpaca_secret_key, cfg.base_url)

    engine = LiveEngine(
        broker=broker,
        symbols=cfg.symbols,
        timeframe=cfg.timeframe,
        rsi_period=cfg.rsi_period,
        rsi_buy_threshold=cfg.rsi_buy_threshold,
        rsi_sell_threshold=cfg.rsi_sell_threshold,
        order_qty=cfg.order_qty,
        long_only=cfg.long_only,
    )

    engine.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
