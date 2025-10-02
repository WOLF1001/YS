from __future__ import annotations

from typing import Dict, Optional

import httpx
import krakenex


class KrakenClient:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self._api = krakenex.API(key=api_key, secret=api_secret)

    def get_balance(self) -> Dict[str, float]:
        response = self._api.query_private("Balance")
        if error := response.get("error"):
            raise RuntimeError(f"Kraken API error: {error}")
        result = response.get("result", {})
        return {asset: float(amount) for asset, amount in result.items()}

    def get_deposit_methods(self, asset: str) -> list[dict]:
        response = self._api.query_private("DepositMethods", {"asset": asset})
        if error := response.get("error"):
            raise RuntimeError(f"Kraken API error: {error}")
        return response.get("result", [])

    def get_deposit_address(self, asset: str, method: Optional[str] = None) -> list[dict]:
        params = {"asset": asset}
        if method:
            params["method"] = method
        response = self._api.query_private("DepositAddresses", params)
        if error := response.get("error"):
            raise RuntimeError(f"Kraken API error: {error}")
        return response.get("result", [])

    def add_order(self, pair: str, type_: str, ordertype: str, volume: str, price: Optional[str] = None) -> dict:
        params = {
            "pair": pair,
            "type": type_,
            "ordertype": ordertype,
            "volume": volume,
        }
        if price is not None:
            params["price"] = price
        response = self._api.query_private("AddOrder", params)
        if error := response.get("error"):
            raise RuntimeError(f"Kraken API error: {error}")
        return response.get("result", {})
