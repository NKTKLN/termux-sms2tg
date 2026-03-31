"""Utilities for fetching and processing JSON records from Termux API commands.

This module provides a small configuration model, a response processor,
and a client wrapper around subprocess-based Termux command execution.
It supports record filtering, field selection, and stable hash generation.
"""

import hashlib
import json
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass
class ResponseProcessingConfig:
    """Configuration for filtering, shaping, and hashing response records.

    Attributes:
        filter_by (dict[str, Any]): Field/value pairs required for a record to pass.
        output_fields (list[str]): Fields to keep in the processed output.
        hash_fields (list[str]): Fields used to build a stable record hash.
    """

    filter_by: dict[str, Any]
    output_fields: list[str]
    hash_fields: list[str]

    def __post_init__(self) -> None:
        """Validate config field types after dataclass initialization.

        Raises:
            TypeError: If any config field has an invalid type.
        """
        if not isinstance(self.filter_by, dict):
            raise TypeError("filter_by must be a dict")
        if not isinstance(self.output_fields, list) or not all(
            isinstance(x, str) for x in self.output_fields
        ):
            raise TypeError("output_fields must be a list of strings")
        if not isinstance(self.hash_fields, list) or not all(
            isinstance(x, str) for x in self.hash_fields
        ):
            raise TypeError("hash_fields must be a list of strings")


class ResponseProcessor:
    """Processes raw Termux records using filter and output rules.

    Args:
        config (ResponseProcessingConfig): Processing configuration.
    """

    def __init__(self, config: ResponseProcessingConfig) -> None:
        """Initialize the processor from a validated config.

        Args:
            config (ResponseProcessingConfig): Processing configuration.
        """
        self.filter_by = config.filter_by
        self.output_fields = config.output_fields
        self.hash_fields = config.hash_fields

    def _build_hash(self, record: dict[str, Any]) -> str:
        """Build a SHA-256 hash for a record.

        Args:
            record (dict[str, Any]): Source record.

        Returns:
            str: Hex-encoded SHA-256 hash.
        """
        if self.hash_fields:
            values = [str(record.get(field, "")) for field in self.hash_fields]
        else:
            values = [str(v) for v in sorted(record.items(), key=lambda item: item[0])]
        raw_string = "|".join(values)
        return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    def process(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter records, select output fields, and append a hash.

        Args:
            records (list[dict[str, Any]]): Raw records to process.

        Returns:
            list[dict[str, Any]]: Processed records that matched the filter.
        """
        processed_records = []

        for record in records:
            if not all(
                record.get(field) == expected
                for field, expected in self.filter_by.items()
            ):
                continue

            processed_record = {
                field: record.get(field, "") for field in self.output_fields
            }
            if not self.output_fields:
                processed_record = dict(record)

            processed_record["hash"] = self._build_hash(record)
            processed_records.append(processed_record)

        return processed_records


class TermuxRecordsClient:
    """Client for fetching and processing JSON records from a Termux command.

    Args:
        command (Sequence[str]): Shell command and arguments to execute.
        processing_config (ResponseProcessingConfig): Record processing config.
    """

    _ALLOWED_COMMANDS = ("termux-call-log", "termux-sms-list")

    def __init__(
        self, command: Sequence[str], processing_config: ResponseProcessingConfig
    ) -> None:
        """Initialize the client.

        Args:
            command (Sequence[str]): Shell command and arguments.
            processing_config (ResponseProcessingConfig): Record processing config.

        Raises:
            TypeError: If command is not a non-string sequence of non-empty strings.
            ValueError: If the command is not supported.
        """
        if not isinstance(command, Sequence) or isinstance(command, str):
            raise TypeError("command must be a non-string sequence of strings")
        if not command or not all(isinstance(part, str) and part for part in command):
            raise TypeError("command must be a non-empty sequence of non-empty strings")
        if command[0] not in self._ALLOWED_COMMANDS:
            raise ValueError(
                f"command must be one of {', '.join(self._ALLOWED_COMMANDS)}"
            )

        self.command = tuple(command)
        self.processor = ResponseProcessor(processing_config)

    def _execute_command(self) -> list[dict[str, Any]]:
        """Run the Termux command and parse its JSON response.

        Returns:
            list[dict[str, Any]]: Parsed list of raw records.

        Raises:
            RuntimeError: If the command fails, times out, returns empty output,
                or produces invalid JSON.
            TypeError: If the parsed JSON is not a list of dictionaries.
        """
        try:
            completed_process = subprocess.run(  # noqa: S603
                self.command, capture_output=True, text=True, check=True, timeout=10
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Command execution failed: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Command execution timed out") from exc

        if not completed_process.stdout.strip():
            raise RuntimeError("Termux API returned an empty response")

        try:
            data = json.loads(completed_process.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError("Termux API returned invalid JSON") from e

        if not isinstance(data, list):
            raise TypeError("Termux API response must be list")
        if not all(isinstance(item, dict) for item in data):
            raise TypeError("Termux API response must be list of dictionaries")

        return data

    def get_records(self) -> list[dict[str, Any]]:
        """Fetch raw records and return processed results.

        Returns:
            list[dict[str, Any]]: Filtered and transformed records.
        """
        raw_records = self._execute_command()
        return self.processor.process(raw_records)
