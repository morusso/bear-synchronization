from __future__ import annotations

import argparse
from pathlib import Path


def existing_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {value}")
    return path


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be positive")
    return parsed
