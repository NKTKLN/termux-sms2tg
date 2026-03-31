"""Application configuration for Termux record polling and bot integration.

This module stores the bot token and predefined processing configurations
for SMS and call log records fetched through Termux API commands.
"""

from .termux_client import ResponseProcessingConfig

HASH_FILE = "hash.json"

BOT_TOKEN = "your_bot_token_here"  # noqa: S105
CHAT_ID = 123456789

TELEGRAM_PROXY = "socks5://user:password@host:port"

SMS_PROCESSING_CONFIG = ResponseProcessingConfig(
    filter_by={"type": "inbox"},
    output_fields=["number", "received", "body"],
    hash_fields=["threadid", "type", "number", "received", "body"],
)
SMS_TERMUX_COMMAND = ["termux-sms-list", "-l", "5"]

CALL_PROCESSING_CONFIG = ResponseProcessingConfig(
    filter_by={"type": "INCOMING"},
    output_fields=["phone_number", "date"],
    hash_fields=["phone_number", "type", "date", "duration", "sim_id"],
)
CALL_TERMUX_COMMAND = ["termux-call-log", "-l", "5"]
