from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from .commands import cmd_status, cmd_sync
from .constants import ENV_PREFIX, PROG_NAME, VERSION
from .formatting import ColorHelpFormatter
from .logging_setup import configure_logging
from .validators import existing_bear2bk_archive, existing_path, positive_int


class BearSyncCLI:
    """Command-line interface for the bear-sync tool.

    Attributes:
        PROG_NAME: Program name shown in help text and used as the logger name.
        VERSION: Program version string reported by ``--version``.
        ENV_PREFIX: Prefix used when reading defaults from environment variables.
        logger: Logger used to report top-level errors.
        parser: The configured argument parser for the CLI.
    """

    PROG_NAME = PROG_NAME
    VERSION = VERSION
    ENV_PREFIX = ENV_PREFIX

    def __init__(self) -> None:
        """Initializes the logger and builds the argument parser."""
        self.logger = logging.getLogger(self.PROG_NAME)
        self.parser = self._build_parser()

    def run(self, argv: list[str] | None = None) -> int:
        """Parses arguments, configures logging, and dispatches to the subcommand.

        Args:
            argv: Command-line arguments to parse. Defaults to ``sys.argv[1:]``
                when ``None``.

        Returns:
            The process exit code: the subcommand's return value, ``130`` if
            interrupted by the user, or ``1`` on an unhandled exception.
        """
        args = self.parser.parse_args(argv)
        configure_logging(args.verbose, args.quiet, args.log_file)

        try:
            return args.func(args)
        except KeyboardInterrupt:
            self.logger.error("interrupted by user")
            return 130
        except Exception as exc:
            self.logger.error("error: %s", exc)
            return 1

    def _env_default(self, name: str, fallback=None):
        """Reads a default value from an environment variable.

        Args:
            name: Suffix appended to ``ENV_PREFIX`` to form the variable name.
            fallback: Value returned if the environment variable is unset.

        Returns:
            The environment variable's value, or ``fallback`` if unset.
        """
        return os.environ.get(f"{self.ENV_PREFIX}{name}", fallback)

    def _build_parser(self) -> argparse.ArgumentParser:
        """Builds the top-level argument parser and its subcommands.

        Returns:
            The fully configured ``argparse.ArgumentParser``.
        """
        parser = argparse.ArgumentParser(
            prog=self.PROG_NAME,
            description="Extensible command-line argument system — example scaffold.",
            epilog=(
                "Examples:\n"
                f"  {self.PROG_NAME} sync --source ./notes --dest ./backup --dry-run\n"
                f"  {self.PROG_NAME} -v status --format json\n"
            ),
            formatter_class=ColorHelpFormatter,
        )
        parser.add_argument("--version", action="version", version=f"{self.PROG_NAME} {self.VERSION}")

        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v", "--verbose", action="count", default=0,
            help="increase log verbosity (repeatable: -vv, -vvv)",
        )
        verbosity.add_argument(
            "-q", "--quiet", action="store_true",
            help="suppress everything except errors",
        )

        parser.add_argument(
            "-c", "--config",
            type=existing_path,
            default=self._env_default("CONFIG"),
            metavar="FILE",
            help=f"path to a config file (defaults to the {self.ENV_PREFIX}CONFIG env var)",
        )
        parser.add_argument(
            "--log-file",
            type=Path,
            default=self._env_default("LOG_FILE"),
            metavar="FILE",
            help="also write logs to the given file",
        )

        subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
        subparsers.required = True

        self._add_sync_subcommand(subparsers)
        self._add_status_subcommand(subparsers)

        return parser

    def _add_sync_subcommand(self, subparsers) -> None:
        """Registers the ``sync`` subcommand and its arguments.

        Args:
            subparsers: Subparsers action returned by
                ``ArgumentParser.add_subparsers``.
        """
        sync = subparsers.add_parser("sync", help="synchronize notes between two .bear2bk backups")
        sync.add_argument(
            "--source", type=existing_bear2bk_archive, required=True,
            help="source .bear2bk archive",
        )
        sync.add_argument(
            "--dest", type=existing_bear2bk_archive, required=True,
            help="destination .bear2bk archive",
        )
        sync.add_argument(
            "--workers", type=positive_int,
            default=int(self._env_default("WORKERS", "4")),
            help="number of worker threads",
        )
        sync.add_argument("--dry-run", action="store_true", help="show what would happen without touching disk")
        sync.add_argument(
            "--include", action="append", default=[], metavar="PATTERN",
            help="file pattern to include (can be given multiple times)",
        )
        sync.add_argument(
            "--show-diff", action="store_true",
            help="list titles of notes that differ between source and dest",
        )
        sync.set_defaults(func=cmd_sync)

    @staticmethod
    def _add_status_subcommand(subparsers) -> None:
        """Registers the ``status`` subcommand and its arguments.

        Args:
            subparsers: Subparsers action returned by
                ``ArgumentParser.add_subparsers``.
        """
        status = subparsers.add_parser("status", help="show sync status")
        status.add_argument(
            "--format", choices=("text", "json"), default="text",
            help="output format",
        )
        status.set_defaults(func=cmd_status)
