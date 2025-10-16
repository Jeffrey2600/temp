from __future__ import annotations

import re
import time
from typing import List, Optional

import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame  # type: ignore


def parse_timeframe(timeframe_str: str) -> TimeFrame:
    """Parse strings like '1Min', '5Min', '1Hour', '1Day' to TimeFrame.
    Falls back to enum attributes for common minute/hour/day when needed.
    """
    m = re.match(r"^(\d+)(Min|Hour|Day)$", timeframe_str)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        try:
            # Newer style: TimeFrame(num, TimeFrameUnit.<unit>)
            from alpaca_trade_api.rest import TimeFrameUnit  # type: ignore

            unit_map = {
                "Min": TimeFrameUnit.Minute,
                "Hour": TimeFrameUnit.Hour,
                "Day": TimeFrameUnit.Day,
            }
            return TimeFrame(num, unit_map[unit])
        except Exception:
            # Older style enum fallback
            if unit == "Min":
                if num == 1:
                    return TimeFrame.Minute
                if num == 5:
                    return TimeFrame(5, "Min")  # type: ignore
                if num == 15:
                    return TimeFrame(15, "Min")  # type: ignore
            if unit == "Hour":
                if num == 1:
                    return TimeFrame.Hour
            if unit == "Day":
                return TimeFrame.Day
    # Last resort sensible default
    return TimeFrame.Minute


class AlpacaBroker:
    def __init__(self, api_key: str, secret_key: str, base_url: str) -> None:
        self.api = REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version="v2")

    def is_market_open(self) -> bool:
        clock = self.api.get_clock()
        return bool(getattr(clock, "is_open", False))

    def get_position_qty(self, symbol: str) -> int:
        try:
            pos = self.api.get_position(symbol)
            qty = int(float(getattr(pos, "qty", 0)))
            return qty
        except Exception:
            return 0

    def get_cash(self) -> float:
        acct = self.api.get_account()
        return float(getattr(acct, "cash", 0.0))

    def cancel_open_orders(self, symbol: Optional[str] = None) -> None:
        orders = self.api.list_orders(status="open")
        for o in orders:
            if symbol is None or getattr(o, "symbol", None) == symbol:
                try:
                    self.api.cancel_order(o.id)
                    # tiny delay to avoid rate-limit bursts
                    time.sleep(0.05)
                except Exception:
                    pass

    def submit_market_order(self, symbol: str, qty: int, side: str) -> str:
        assert side in {"buy", "sell"}
        order = self.api.submit_order(
            symbol=symbol,
            qty=str(qty),
            side=side,
            type="market",
            time_in_force="day",
        )
        return getattr(order, "id", "")

    def close_position_if_any(self, symbol: str) -> None:
        try:
            self.api.close_position(symbol)
        except Exception:
            pass

    def get_recent_closes(self, symbol: str, timeframe: TimeFrame, limit: int) -> List[float]:
        bars = self.api.get_bars(symbol, timeframe, limit=limit)
        # Handle both DataFrame and list-like responses
        closes: List[float] = []
        if hasattr(bars, "df"):
            df = bars.df  # type: ignore[attr-defined]
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Single symbol sometimes returns MultiIndex (symbol, time)
                try:
                    if isinstance(df.index, pd.MultiIndex):
                        df = df.xs(symbol)
                except Exception:
                    pass
                if "close" in df.columns:
                    closes = [float(x) for x in df["close"].tolist()]
        else:
            # Assume iterable of bar objects with c/close attributes
            for b in bars:
                c = getattr(b, "c", None)
                if c is None:
                    c = getattr(b, "close", None)
                if c is not None:
                    closes.append(float(c))
        return closes
