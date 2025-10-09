from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class KrakenConfig:
    api_key: str
    api_secret: str


@dataclass
class LegionConfig:
    # Placeholder pending API details
    base_url: Optional[str] = None
    api_key: Optional[str] = None


@dataclass
class AppConfig:
    kraken: Optional[KrakenConfig] = None
    legion: Optional[LegionConfig] = None
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    slack_dm_recipient_ids: Optional[str] = None


def load_config(env_path: Optional[str] = None) -> AppConfig:
    if env_path and os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=False)

    kraken_key = os.getenv("KRAKEN_API_KEY")
    kraken_secret = os.getenv("KRAKEN_API_SECRET")

    kraken_cfg = None
    if kraken_key and kraken_secret:
        kraken_cfg = KrakenConfig(api_key=kraken_key, api_secret=kraken_secret)

    legion_cfg = LegionConfig(
        base_url=os.getenv("LEGION_BASE_URL"),
        api_key=os.getenv("LEGION_API_KEY"),
    )

    return AppConfig(
        kraken=kraken_cfg,
        legion=legion_cfg,
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
        slack_app_token=os.getenv("SLACK_APP_TOKEN"),
        slack_dm_recipient_ids=os.getenv("SLACK_DM_RECIPIENT_IDS"),
    )
