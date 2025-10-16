from __future__ import annotations

from typing import Iterable, List, Optional


def compute_rsi(closes: Iterable[float], period: int = 14) -> List[Optional[float]]:
    """Compute Wilder's RSI for the given close series.

    Returns a list of RSI values aligned with the input, with None where
    RSI is not yet defined (first period elements).
    """
    prices = [float(x) for x in closes]
    if period <= 0:
        raise ValueError("RSI period must be positive")
    if len(prices) < period + 1:
        return [None] * len(prices)

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]

    # Initial average gain/loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi: List[Optional[float]] = [None] * len(prices)

    # First RSI value at index period
    rs = (avg_gain / avg_loss) if avg_loss != 0 else float("inf")
    rsi_val = 100.0 - (100.0 / (1.0 + rs)) if rs != float("inf") else 100.0
    rsi[period] = rsi_val

    # Wilder's smoothing for subsequent points
    for i in range(period + 1, len(prices)):
        gain = gains[i - 1]
        loss = losses[i - 1]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi_val = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100.0 - (100.0 / (1.0 + rs))
        rsi[i] = rsi_val

    return rsi


def compute_last_rsi(closes: Iterable[float], period: int = 14) -> Optional[float]:
    values = compute_rsi(closes, period)
    if not values:
        return None
    # Return last non-None value
    for v in reversed(values):
        if v is not None:
            return v
    return None
