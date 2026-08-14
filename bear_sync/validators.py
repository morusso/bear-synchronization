from __future__ import annotations

import argparse
from pathlib import Path

from .constants import BEAR_ARCHIVE_SUFFIX


def existing_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {value}")
    return path


def _bear2bk_suffix(path: Path, value: str) -> None:
    if path.suffix != BEAR_ARCHIVE_SUFFIX:
        raise argparse.ArgumentTypeError(
            f"expected a {BEAR_ARCHIVE_SUFFIX} archive, got: {value}"
        )


def existing_bear2bk_archive(value: str) -> Path:
    path = existing_path(value)
    _bear2bk_suffix(path, value)
    return path


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be positive")
    return parsed
