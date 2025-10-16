import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    alpaca_api_key: str
    alpaca_api_secret: str
    alpaca_base_url: str  # e.g. https://paper-api.alpaca.markets or https://api.alpaca.markets
    alpaca_data_base_url: str  # e.g. https://data.alpaca.markets
    symbol: str           # e.g. AAPL
    time_frame: str       # e.g. 1Min, 5Min, 15Min
    rsi_period: int       # e.g. 14
    rsi_buy_threshold: float  # e.g. 30.0
    rsi_sell_threshold: float # e.g. 70.0
    position_size_usd: float  # e.g. 100.0 per trade
    poll_seconds: int     # e.g. 60 for 1-minute bars


def load_settings() -> Settings:
    missing = []
    def env(name: str, default: str | None = None) -> str:
        val = os.getenv(name, default)
        if val is None:
            missing.append(name)
        return val  # type: ignore

    settings = Settings(
        alpaca_api_key=env("ALPACA_API_KEY", ""),
        alpaca_api_secret=env("ALPACA_API_SECRET", ""),
        alpaca_base_url=env("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        alpaca_data_base_url=env("ALPACA_DATA_BASE_URL", "https://data.alpaca.markets"),
        symbol=env("SYMBOL", "AAPL"),
        time_frame=env("TIME_FRAME", "1Min"),
        rsi_period=int(env("RSI_PERIOD", "14")),
        rsi_buy_threshold=float(env("RSI_BUY_THRESHOLD", "30")),
        rsi_sell_threshold=float(env("RSI_SELL_THRESHOLD", "70")),
        position_size_usd=float(env("POSITION_SIZE_USD", "100")),
        poll_seconds=int(env("POLL_SECONDS", "60")),
    )

    if missing:
        # We allow defaults for most, but warn if keys are empty
        if not settings.alpaca_api_key or not settings.alpaca_api_secret:
            print("Warning: ALPACA_API_KEY/ALPACA_API_SECRET not set. Set them to trade.")
    return settings
