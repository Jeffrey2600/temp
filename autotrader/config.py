from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional; continue if not installed
    pass


@dataclass
class Config:
    alpaca_api_key: str
    alpaca_secret_key: str
    paper: bool
    base_url: str

    symbols: List[str]
    timeframe: str  # e.g., "1Min"

    rsi_period: int
    rsi_buy_threshold: float
    rsi_sell_threshold: float

    order_qty: int
    poll_interval_sec: int
    long_only: bool = True


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y"}


def _get_base_url(paper: bool) -> str:
    return "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"


def _parse_symbols(value: str | None) -> List[str]:
    if not value:
        return ["AAPL"]
    symbols = [s.strip().upper() for s in value.split(",") if s.strip()]
    return symbols or ["AAPL"]


def load_config() -> Config:
    paper = _bool_env("ALPACA_PAPER", True)
    cfg = Config(
        alpaca_api_key=os.getenv("ALPACA_API_KEY", ""),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
        paper=paper,
        base_url=_get_base_url(paper),
        symbols=_parse_symbols(os.getenv("SYMBOLS")),
        timeframe=os.getenv("TIMEFRAME", "1Min"),
        rsi_period=int(os.getenv("RSI_PERIOD", "14")),
        rsi_buy_threshold=float(os.getenv("RSI_BUY_THRESHOLD", "30")),
        rsi_sell_threshold=float(os.getenv("RSI_SELL_THRESHOLD", "70")),
        order_qty=int(os.getenv("ORDER_QTY", "1")),
        poll_interval_sec=int(os.getenv("POLL_INTERVAL_SEC", "5")),
    )
    if not cfg.alpaca_api_key or not cfg.alpaca_secret_key:
        raise RuntimeError(
            "Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment."
        )
    return cfg
