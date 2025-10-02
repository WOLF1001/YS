from __future__ import annotations

from typing import Optional

import httpx


class LegionClient:
    def __init__(self, base_url: Optional[str], api_key: Optional[str]) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.Client(base_url=base_url) if base_url else None

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    # TODO: Define deposit and sales endpoints once API is available
