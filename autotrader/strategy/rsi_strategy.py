from dataclasses import dataclass
from typing import Optional


@dataclass
class Signal:
    action: Optional[str]  # 'buy', 'sell', or None
    reason: str


def rsi_signal(rsi_values: list[float], buy_threshold: float, sell_threshold: float) -> Signal:
    if len(rsi_values) < 2:
        return Signal(action=None, reason="insufficient_rsi")

    prev_rsi = rsi_values[-2]
    latest_rsi = rsi_values[-1]

    # Buy when RSI crosses above buy_threshold from below
    if prev_rsi <= buy_threshold < latest_rsi:
        return Signal(action="buy", reason=f"rsi_cross_up:{prev_rsi:.2f}->{latest_rsi:.2f}")

    # Sell when RSI crosses below sell_threshold from above
    if prev_rsi >= sell_threshold > latest_rsi:
        return Signal(action="sell", reason=f"rsi_cross_down:{prev_rsi:.2f}->{latest_rsi:.2f}")

    return Signal(action=None, reason="hold")
