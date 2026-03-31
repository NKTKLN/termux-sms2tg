"""Utilities for persistent storage of processed record hashes.

This module provides a small file-based storage class for tracking hashes
of already processed records. It supports loading hashes from JSON,
checking for duplicates, and saving updated values back to disk.
"""

import json
from pathlib import Path


class HashStorage:
    """Stores processed record hashes in a JSON file.

    Args:
        filename (str): Path to the JSON file used for hash persistence.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the hash storage.

        Args:
            filename (str): Path to the JSON file used for hash persistence.
        """
        self.filename = Path(filename)
        self.hashes = self._load()

    def _load(self) -> set[str]:
        """Load hashes from the JSON storage file.

        Returns:
            set[str]: Stored hash values. Returns an empty set if the file does
                not exist, cannot be read, or contains invalid data.
        """
        if not self.filename.exists():
            return set()

        try:
            with self.filename.open(encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return {str(item) for item in data}
            else:
                return set()
        except (json.JSONDecodeError, OSError):
            return set()

    def _save(self) -> None:
        """Save current hashes to the JSON storage file.

        Raises:
            OSError: If the storage file cannot be written.
        """
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(list(self.hashes), file, ensure_ascii=False, indent=2)

    def check_and_add(self, hash_value: str) -> bool:
        """Check whether a hash is new and persist it if so.

        Args:
            hash_value (str): Hash value to check and store.

        Returns:
            bool: True if the hash was new and added, False if it already
                existed.
        """
        if hash_value in self.hashes:
            return False

        self.hashes.add(hash_value)
        self._save()
        return True
