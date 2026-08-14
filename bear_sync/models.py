from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncArgs:
    source: Path
    dest: Path
    workers: int
    dry_run: bool
    include: list[str]
