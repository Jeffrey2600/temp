from collections import deque
from typing import Deque, Iterable, List


def compute_rsi(prices: Iterable[float], period: int = 14) -> List[float]:
    prices_list = list(prices)
    if len(prices_list) < period + 1:
        return []

    gains: Deque[float] = deque(maxlen=period)
    losses: Deque[float] = deque(maxlen=period)
    rsis: List[float] = []

    # seed
    for i in range(1, period + 1):
        delta = prices_list[i] - prices_list[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    def rsi_from(avg_gain: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    rsis.append(rsi_from(avg_gain, avg_loss))

    # rolling
    for i in range(period + 1, len(prices_list)):
        delta = prices_list[i] - prices_list[i - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rsis.append(rsi_from(avg_gain, avg_loss))

    return rsis
