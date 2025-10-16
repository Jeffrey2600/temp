from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional

from autotrader.indicators import compute_rsi


Signal = Optional[Literal["buy", "sell"]]


@dataclass
class RSIStrategyConfig:
    period: int = 14
    buy_threshold: float = 30.0
    sell_threshold: float = 70.0
    long_only: bool = True


class RSIStrategy:
    def __init__(self, config: RSIStrategyConfig) -> None:
        self.config = config

    def decide(self, closes: Iterable[float]) -> Signal:
        rsi_values = compute_rsi(closes, self.config.period)
        if len(rsi_values) < self.config.period + 2:
            return None
        # Need last two RSI values for cross detection
        rsi_prev = rsi_values[-2]
        rsi_curr = rsi_values[-1]
        if rsi_prev is None or rsi_curr is None:
            return None

        # Cross above buy threshold => buy signal
        if rsi_prev <= self.config.buy_threshold < rsi_curr:
            return "buy"

        # Cross below sell threshold => sell signal (exit)
        if rsi_prev >= self.config.sell_threshold > rsi_curr:
            return "sell"

        return None
