from __future__ import annotations

import argparse
import logging

from .constants import PROG_NAME
from .models import SyncArgs

logger = logging.getLogger(PROG_NAME)


def cmd_sync(args: argparse.Namespace) -> int:
    payload = SyncArgs(args.source, args.dest, args.workers, args.dry_run, args.include)
    logger.info("sync: %s -> %s (workers=%d, dry_run=%s)",
                payload.source, payload.dest, payload.workers, payload.dry_run)
    if payload.include:
        logger.debug("include filters: %s", payload.include)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if args.format == "json":
        print('{"status": "idle"}')
    else:
        print("status: idle")
    return 0
