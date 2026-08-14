from __future__ import annotations

import argparse
import logging
import tempfile
from pathlib import Path

from .backup import BearBackupArchive
from .compare import compare_archives
from .constants import PROG_NAME
from .models import SyncArgs

logger = logging.getLogger(PROG_NAME)


def cmd_sync(args: argparse.Namespace) -> int:
    payload = SyncArgs(args.source, args.dest, args.workers, args.dry_run, args.include)
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

    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if args.format == "json":
        print('{"status": "idle"}')
    else:
        print("status: idle")
    return 0
