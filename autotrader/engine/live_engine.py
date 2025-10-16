from __future__ import annotations

import logging
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List

from autotrader.broker import AlpacaBroker, parse_timeframe
from autotrader.strategy import RSIStrategy, RSIStrategyConfig


logger = logging.getLogger("autotrader.engine")


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _sleep_until_next_minute(pad_seconds: float = 1.0) -> None:
    now = _utc_now()
    next_minute = (now.replace(second=0, microsecond=0) + timedelta(minutes=1))
    to_sleep = (next_minute - now).total_seconds() + pad_seconds
    if to_sleep > 0:
        time.sleep(to_sleep)


class LiveEngine:
    def __init__(
        self,
        broker: AlpacaBroker,
        symbols: List[str],
        timeframe: str = "1Min",
        rsi_period: int = 14,
        rsi_buy_threshold: float = 30.0,
        rsi_sell_threshold: float = 70.0,
        order_qty: int = 1,
        long_only: bool = True,
    ) -> None:
        self.broker = broker
        self.symbols = symbols
        self.tf_str = timeframe
        self.tf = parse_timeframe(timeframe)
        self.order_qty = order_qty
        self.long_only = long_only
        self.strategy = RSIStrategy(
            RSIStrategyConfig(
                period=rsi_period,
                buy_threshold=rsi_buy_threshold,
                sell_threshold=rsi_sell_threshold,
                long_only=long_only,
            )
        )
        self._stop = False

    def _handle_sigint(self, *_args) -> None:
        logger.info("Received signal, stopping...")
        self._stop = True

    def run(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigint)

        logger.info("Starting live engine for symbols=%s timeframe=%s qty=%s", self.symbols, self.tf_str, self.order_qty)

        # Pre-compute how many bars are needed
        min_bars = max(100, self.strategy.config.period + 5)

        while not self._stop:
            try:
                if not self.broker.is_market_open():
                    logger.info("Market is closed. Sleeping until next minute...")
                    _sleep_until_next_minute(pad_seconds=1.0)
                    continue

                for symbol in self.symbols:
                    closes = self.broker.get_recent_closes(symbol, self.tf, limit=min_bars)
                    if len(closes) < self.strategy.config.period + 2:
                        logger.debug("%s: not enough bars (%d)", symbol, len(closes))
                        continue

                    signal_decision = self.strategy.decide(closes)
                    pos_qty = self.broker.get_position_qty(symbol)

                    if signal_decision == "buy":
                        if self.long_only and pos_qty > 0:
                            logger.info("%s: already long (%d), skip buy", symbol, pos_qty)
                        else:
                            logger.info("%s: BUY %d (RSI cross above %.1f)", symbol, self.order_qty, self.strategy.config.buy_threshold)
                            try:
                                self.broker.cancel_open_orders(symbol)
                                self.broker.submit_market_order(symbol, self.order_qty, "buy")
                            except Exception as e:
                                logger.exception("%s: buy order failed: %s", symbol, e)

                    elif signal_decision == "sell":
                        if pos_qty > 0:
                            logger.info("%s: SELL to exit (%d) (RSI cross below %.1f)", symbol, pos_qty, self.strategy.config.sell_threshold)
                            try:
                                self.broker.cancel_open_orders(symbol)
                                self.broker.submit_market_order(symbol, pos_qty, "sell")
                            except Exception as e:
                                logger.exception("%s: sell order failed: %s", symbol, e)
                        else:
                            logger.info("%s: no long position to exit", symbol)
                    else:
                        logger.debug("%s: no action", symbol)

                _sleep_until_next_minute(pad_seconds=1.0)

            except Exception as e:
                logger.exception("Engine loop error: %s", e)
                time.sleep(3)

        logger.info("Engine stopped.")
