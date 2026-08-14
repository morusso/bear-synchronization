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
    show_diff: bool


@dataclass
class ArchiveComparison:
    common: set[str]
    only_in_source: set[str]
    only_in_dest: set[str]
