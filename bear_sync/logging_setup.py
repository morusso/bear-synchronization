from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(verbose: int, quiet: bool, log_file: Path | None) -> None:
    """Configures the root logger's level, format, and handlers.

    Args:
        verbose: Verbosity count from repeated ``-v`` flags. ``1`` enables
            INFO, ``2`` or more enables DEBUG.
        quiet: If ``True``, restricts logging to ERROR and above,
            overriding ``verbose``.
        log_file: Optional path to also write logs to, in addition to stderr.
    """
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
        force=True,
    )
