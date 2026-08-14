from __future__ import annotations

import argparse
import logging
import tempfile
from pathlib import Path

from .backup import BearBackupArchive
from .compare import compare_archives
from .constants import PROG_NAME
from .merge import fill_missing_notes
from .models import ArchiveComparison, SyncArgs

logger = logging.getLogger(PROG_NAME)


def cmd_sync(args: argparse.Namespace) -> int:
    """Synchronizes notes between two ``.bear2bk`` archives.

    Extracts both archives to temporary directories, compares their note
    titles, fills notes missing on either side into the other, and repacks
    any archive that was modified (backing it up first).

    Args:
        args: Parsed CLI namespace with ``source``, ``dest``, ``workers``,
            ``dry_run``, ``include``, and ``show_diff`` attributes.

    Returns:
        ``0`` on success, regardless of whether any notes were copied.
    """
    payload = SyncArgs(
        args.source, args.dest, args.workers, args.dry_run, args.include, args.show_diff,
    )
    logger.info("sync: %s -> %s (workers=%d, dry_run=%s)",
                payload.source, payload.dest, payload.workers, payload.dry_run)
    if payload.include:
        logger.debug("include filters: %s", payload.include)

    with tempfile.TemporaryDirectory() as source_tmp, tempfile.TemporaryDirectory() as dest_tmp:
        source_root = BearBackupArchive.extract(payload.source, Path(source_tmp))
        dest_root = BearBackupArchive.extract(payload.dest, Path(dest_tmp))
        comparison = compare_archives(source_root, dest_root)

        logger.info("notes in both archives: %d", len(comparison.common))
        logger.info("notes only in source: %d", len(comparison.only_in_source))
        logger.info("notes only in dest: %d", len(comparison.only_in_dest))
        logger.debug("common: %s", sorted(comparison.common))
        logger.debug("only in source: %s", sorted(comparison.only_in_source))
        logger.debug("only in dest: %s", sorted(comparison.only_in_dest))

        if payload.show_diff:
            _print_diff(comparison)

        merge_result = fill_missing_notes(
            source_root, dest_root, comparison,
            include=payload.include, dry_run=payload.dry_run,
        )

        if not merge_result.added_to_source and not merge_result.added_to_dest:
            logger.info("archives already in sync, nothing to fill in")
            return 0

        if payload.dry_run:
            logger.info(
                "dry-run: would add %d note(s) to dest, %d note(s) to source",
                len(merge_result.added_to_dest), len(merge_result.added_to_source),
            )
            return 0

        if merge_result.added_to_dest:
            BearBackupArchive.backup(payload.dest)
            BearBackupArchive.repack(dest_root, payload.dest)
            logger.info("updated %s (+%d note(s))", payload.dest, len(merge_result.added_to_dest))

        if merge_result.added_to_source:
            BearBackupArchive.backup(payload.source)
            BearBackupArchive.repack(source_root, payload.source)
            logger.info("updated %s (+%d note(s))", payload.source, len(merge_result.added_to_source))

    return 0


def _print_diff(comparison: ArchiveComparison) -> None:
    """Prints the titles of notes unique to the source and destination archives.

    Args:
        comparison: Result of comparing the two archives' note titles.
    """
    print(f"Only in source ({len(comparison.only_in_source)}):")
    for title in sorted(comparison.only_in_source):
        print(f"  - {title}")

    print(f"Only in dest ({len(comparison.only_in_dest)}):")
    for title in sorted(comparison.only_in_dest):
        print(f"  - {title}")


def cmd_status(args: argparse.Namespace) -> int:
    """Prints the current sync status.

    Args:
        args: Parsed CLI namespace with a ``format`` attribute (``"text"``
            or ``"json"``).

    Returns:
        ``0`` on success.
    """
    if args.format == "json":
        print('{"status": "idle"}')
    else:
        print("status: idle")
    return 0
