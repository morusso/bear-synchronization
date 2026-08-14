from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncArgs:
    """Parsed arguments for the ``sync`` subcommand.

    Attributes:
        source: Path to the source ``.bear2bk`` archive.
        dest: Path to the destination ``.bear2bk`` archive.
        workers: Number of worker threads to use.
        dry_run: Whether to only report what would happen without touching disk.
        include: Glob-style patterns restricting which notes are synced.
        show_diff: Whether to print the titles of notes that differ.
    """

    source: Path
    dest: Path
    workers: int
    dry_run: bool
    include: list[str]
    show_diff: bool


@dataclass
class ArchiveComparison:
    """Result of comparing note titles between two archives.

    Attributes:
        common: Titles present in both archives.
        only_in_source: Titles present only in the source archive.
        only_in_dest: Titles present only in the destination archive.
    """

    common: set[str]
    only_in_source: set[str]
    only_in_dest: set[str]


@dataclass
class MergeResult:
    """Result of filling missing notes between two archives.

    Attributes:
        added_to_source: Titles of notes copied into the source archive.
        added_to_dest: Titles of notes copied into the destination archive.
    """

    added_to_source: set[str]
    added_to_dest: set[str]
