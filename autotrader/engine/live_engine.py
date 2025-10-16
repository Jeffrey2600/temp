import math
import time
from typing import List

from autotrader.broker.alpaca import AlpacaBroker, Order
from autotrader.indicators.rsi import compute_rsi
from autotrader.strategy.rsi_strategy import rsi_signal


class LiveEngine:
    def __init__(self, broker: AlpacaBroker, symbol: str, timeframe: str, rsi_period: int,
                 buy_threshold: float, sell_threshold: float, position_size_usd: float, poll_seconds: int):
        self.broker = broker
        self.symbol = symbol
        self.timeframe = timeframe
        self.rsi_period = rsi_period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.position_size_usd = position_size_usd
        self.poll_seconds = poll_seconds

    def run_forever(self) -> None:
        print(f"Starting live engine for {self.symbol} @ {self.timeframe}")
        while True:
            try:
                bars = self.broker.get_latest_bars(self.symbol, self.timeframe, limit=max(200, self.rsi_period + 10))
                closes: List[float] = [float(b["c"]) for b in bars]
                rsis = compute_rsi(closes, self.rsi_period)
                signal = rsi_signal(rsis, self.buy_threshold, self.sell_threshold)

                last_price = closes[-1] if closes else None
                positions = self.broker.get_positions(self.symbol)
                qty_held = float(positions[0]["qty"] if positions else 0)

                print({
                    "price": last_price,
                    "rsi": rsis[-1] if rsis else None,
                    "signal": signal.__dict__,
                    "qty_held": qty_held,
                })

                if last_price is None:
                    time.sleep(self.poll_seconds)
                    continue

                if signal.action == "buy" and qty_held == 0:
                    qty = max(1, math.floor(self.position_size_usd / last_price))
                    order = Order(symbol=self.symbol, qty=str(qty), side="buy", type="market", time_in_force="day")
                    resp = self.broker.submit_order(order)
                    print({"placed_buy": resp})
                elif signal.action == "sell" and qty_held > 0:
                    order = Order(symbol=self.symbol, qty=str(int(qty_held)), side="sell", type="market", time_in_force="day")
                    resp = self.broker.submit_order(order)
                    print({"placed_sell": resp})

            except Exception as e:
                print({"error": str(e)})

            time.sleep(self.poll_seconds)
