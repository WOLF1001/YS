from __future__ import annotations

import os
import logging
from typing import List

from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app import App


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_user_ids_from_env(value: str | None) -> List[str]:
    if not value:
        return []
    # Accept comma or spaces as separators
    separators = [",", " ", "\n", "\t", ";"]
    result: List[str] = [value]
    for sep in separators:
        next_result: List[str] = []
        for chunk in result:
            next_result.extend([c.strip() for c in chunk.split(sep) if c.strip()])
        result = next_result
    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: List[str] = []
    for item in result:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def build_app() -> App:
    app = App(token=os.environ["SLACK_BOT_TOKEN"])  # requires channels:read, chat:write, im:history

    @app.event("app_mention")
    def handle_app_mention_events(body, say):
        user_id = body.get("event", {}).get("user")
        text = body.get("event", {}).get("text", "").strip()
        forward_message_to_recipients(app, user_id=user_id, text=text)
        say("Дякую! Я повідомив відповідальних.")

    @app.event("message")
    def handle_dm_events(body, say):
        event = body.get("event", {})
        # Only react to direct user messages in DMs
        if event.get("channel_type") != "im":
            return
        if event.get("subtype") is not None:
            return
        if event.get("bot_id"):
            return
        user_id = event.get("user")
        text = (event.get("text") or "").strip()
        if not user_id or not text:
            return
        forward_message_to_recipients(app, user_id=user_id, text=text)
        say("Дякую! Я повідомив відповідальних.")

    return app


def forward_message_to_recipients(app: App, user_id: str | None, text: str) -> None:
    recipients = parse_user_ids_from_env(os.getenv("SLACK_DM_RECIPIENT_IDS"))
    if not recipients:
        logger.warning("No recipients configured in SLACK_DM_RECIPIENT_IDS")
        return

    # Build a standardized message that preserves the user's original text
    user_mention = f"<@{user_id}>" if user_id else "Користувач"
    message = f"Користувач {user_mention} повідомив(ла): \"{text}\""

    for recipient_id in recipients:
        try:
            # Open a DM and post the message
            open_resp = app.client.conversations_open(users=recipient_id)
            channel_id = open_resp["channel"]["id"]
            app.client.chat_postMessage(channel=channel_id, text=message)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to send DM to %s: %s", recipient_id, exc)


def main() -> None:
    # Load .env if present
    load_dotenv(override=False)

    # Required tokens
    app_token = os.getenv("SLACK_APP_TOKEN")  # xapp-... for Socket Mode
    bot_token = os.getenv("SLACK_BOT_TOKEN")  # xoxb-...

    if not app_token or not bot_token:
        raise SystemExit(
            "SLACK_APP_TOKEN and SLACK_BOT_TOKEN must be set. "
            "Also configure SLACK_DM_RECIPIENT_IDS as comma-separated user IDs."
        )

    app = build_app()
    handler = SocketModeHandler(app, app_token)
    logger.info("Starting Slack bot in Socket Mode...")
    handler.start()


if __name__ == "__main__":
    main()
