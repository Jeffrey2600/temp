from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class Order:
    symbol: str
    qty: str
    side: str  # 'buy' or 'sell'
    type: str  # 'market'
    time_in_force: str  # 'day' or 'gtc'


class AlpacaBroker:
    def __init__(self, api_key: str, api_secret: str, base_url: str, data_base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.data_base_url = data_base_url.rstrip('/')
        self.account_url = f"{self.base_url}/v2/account"
        self.orders_url = f"{self.base_url}/v2/orders"
        self.bars_url = f"{self.data_base_url}/v2/stocks/bars"
        self.positions_url = f"{self.base_url}/v2/positions"

    def _headers(self) -> dict:
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_account(self) -> dict:
        resp = requests.get(self.account_url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_positions(self, symbol: Optional[str] = None) -> list[dict]:
        url = self.positions_url if symbol is None else f"{self.positions_url}/{symbol}"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            return [data]
        return data

    def submit_order(self, order: Order) -> dict:
        payload = {
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "time_in_force": order.time_in_force,
        }
        resp = requests.post(self.orders_url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_latest_bars(self, symbol: str, timeframe: str, limit: int = 100) -> list[dict]:
        # Alpaca v2 bars endpoint requires params: symbols, timeframe, limit
        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "limit": limit,
            "adjustment": "raw",
        }
        resp = requests.get(self.bars_url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Response schema: { "bars": { "AAPL": [ {"t":..., "o":..., "h":..., "l":..., "c":..., "v":...}, ... ] } }
        bars = data.get("bars", {}).get(symbol, [])
        return bars
