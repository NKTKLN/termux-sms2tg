"""Utilities for sending SMS and call notifications through Telegram.

This module provides a small wrapper around the Telegram Bot API for
sending formatted notifications about new SMS messages and incoming calls.
"""

from typing import Any

import telebot
from telebot.apihelper import ApiException


class TelegramNotifier:
    """Sends formatted SMS and call notifications to a Telegram chat.

    Args:
        token (str): Telegram bot token.
        chat_id (int): Target chat identifier for notifications.
    """

    SMS_NOTIFICATION_MESSAGE = (
        "📩 *New SMS received*\n"
        "*From:* `{number}`\n"
        "*Received:* `{received}`\n"
        "*Message:*\n"
        "```{body}```"
    )

    CALL_NOTIFICATION_MESSAGE = (
        "📞 *New incoming call*\n*From:* `{phone_number}`\n*Date:* `{date}`"
    )

    def __init__(self, token: str, chat_id: int, proxy: str | None = None) -> None:
        """Initialize the Telegram notifier.

        Args:
            token (str): Telegram bot token.
            chat_id (int): Target chat identifier for notifications.
            proxy (str | None): Optional HTTPS proxy URL for Telegram requests.
        """
        if proxy is not None:
            telebot.apihelper.proxy = {"https": proxy}

        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id

    def sms_notify(self, data: dict[str, Any]) -> None:
        """Send a notification about a newly received SMS message.

        Args:
            data (dict[str, Any]): SMS record data.

        Raises:
            RuntimeError: If sending the Telegram message fails.
        """
        try:
            message = self.SMS_NOTIFICATION_MESSAGE.format(
                number=data.get("number", "---"),
                received=data.get("received", "---"),
                body=data.get("body", "---"),
            )
            self.bot.send_message(self.chat_id, message, parse_mode="Markdown")
        except ApiException as exc:
            raise RuntimeError(f"Failed to send SMS notification: {exc}") from exc

    def call_notify(self, data: dict[str, Any]) -> None:
        """Send a notification about a new incoming call.

        Args:
            data (dict[str, Any]): Call record data.

        Raises:
            RuntimeError: If sending the Telegram message fails.
        """
        try:
            message = self.CALL_NOTIFICATION_MESSAGE.format(
                phone_number=data.get("phone_number", "---"),
                date=data.get("date", "---"),
            )
            self.bot.send_message(self.chat_id, message, parse_mode="Markdown")
        except ApiException as exc:
            raise RuntimeError(f"Failed to send call notification: {exc}") from exc
