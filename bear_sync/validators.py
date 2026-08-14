from __future__ import annotations

import argparse
from pathlib import Path

from .constants import BEAR_ARCHIVE_SUFFIX


def existing_path(value: str) -> Path:
    """Parses and validates a CLI argument as an existing filesystem path.

    Args:
        value: Raw string value passed on the command line.

    Returns:
        The expanded path.

    Raises:
        argparse.ArgumentTypeError: If the path does not exist.
    """
    path = Path(value).expanduser()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {value}")
    return path


def _bear2bk_suffix(path: Path, value: str) -> None:
    """Checks that a path has the ``.bear2bk`` suffix.

    Args:
        path: Path to check.
        value: Original raw string value, used in the error message.

    Raises:
        argparse.ArgumentTypeError: If ``path`` does not have the
            ``.bear2bk`` suffix.
    """
    if path.suffix != BEAR_ARCHIVE_SUFFIX:
        raise argparse.ArgumentTypeError(
            f"expected a {BEAR_ARCHIVE_SUFFIX} archive, got: {value}"
        )


def existing_bear2bk_archive(value: str) -> Path:
    """Parses and validates a CLI argument as an existing ``.bear2bk`` archive.

    Args:
        value: Raw string value passed on the command line.

    Returns:
        The expanded path to the archive.

    Raises:
        argparse.ArgumentTypeError: If the path does not exist or does not
            have the ``.bear2bk`` suffix.
    """
    path = existing_path(value)
    _bear2bk_suffix(path, value)
    return path


def positive_int(value: str) -> int:
    """Parses and validates a CLI argument as a positive integer.

    Args:
        value: Raw string value passed on the command line.

    Returns:
        The parsed integer.

    Raises:
        argparse.ArgumentTypeError: If ``value`` is not an integer or is
            not positive.
    """
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be positive")
    return parsed
