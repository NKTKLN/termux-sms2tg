"""Main polling loop for Termux SMS and call notifications.

This module initializes the Telegram notifier, Termux API clients,
hash storage, and application logger, then continuously polls for new
SMS messages and incoming calls. New records are detected by their
hashes and sent to Telegram.
"""

import logging
from time import sleep

from .bot import TelegramNotifier
from .config import (
    BOT_TOKEN,
    CALL_PROCESSING_CONFIG,
    CALL_TERMUX_COMMAND,
    CHAT_ID,
    HASH_FILE,
    SMS_PROCESSING_CONFIG,
    SMS_TERMUX_COMMAND,
    TELEGRAM_PROXY,
)
from .hash import HashStorage
from .termux_client import TermuxRecordsClient

logger = logging.getLogger(__name__)


def main() -> None:  # noqa: C901
    """Run the notification polling loop.

    The function creates clients for SMS and call log retrieval, restores
    previously seen record hashes, and polls Termux API commands in an
    infinite loop. Only records with new hashes are sent as Telegram
    notifications.
    """
    logger.info("starting termux notification service")

    telegram_notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID, TELEGRAM_PROXY)
    sms_client = TermuxRecordsClient(SMS_TERMUX_COMMAND, SMS_PROCESSING_CONFIG)
    call_client = TermuxRecordsClient(CALL_TERMUX_COMMAND, CALL_PROCESSING_CONFIG)
    hash_storage = HashStorage(HASH_FILE)

    logger.info("initialization completed successfully")

    while True:
        try:
            sms_records = sms_client.get_records()
        except Exception:
            logger.exception("failed to fetch sms records")
            sms_records = []

        try:
            call_records = call_client.get_records()
        except Exception:
            logger.exception("failed to fetch call records")
            call_records = []

        for sms_record in sms_records:
            try:
                record_hash = sms_record.get("hash")
                if not isinstance(record_hash, str):
                    logger.warning("skipped sms record without valid hash")
                    continue
                if not hash_storage.check_and_add(record_hash):
                    logger.debug("skipped already processed sms record")
                    continue

                logger.info(
                    f"sending sms notification for number "
                    f"{sms_record.get('number', '---')}"
                )
                telegram_notifier.sms_notify(sms_record)
            except Exception:
                logger.exception("failed to process sms record")

        for call_record in call_records:
            try:
                record_hash = call_record.get("hash")
                if not isinstance(record_hash, str):
                    logger.warning("skipped call record without valid hash")
                    continue
                if not hash_storage.check_and_add(record_hash):
                    logger.debug("skipped already processed call record")
                    continue

                logger.info(
                    f"sending call notification for phone number "
                    f"{call_record.get('phone_number', '---')}"
                )
                telegram_notifier.call_notify(call_record)
            except Exception:
                logger.exception("failed to process call record")

        sleep(5)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
