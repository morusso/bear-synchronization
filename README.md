# bear-sync

![Language](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A CLI tool for synchronizing notes between two [Bear](https://bear.app) app backups in `.bear2bk` format.

## Assumptions

- **Input format**: a Bear backup (`.bear2bk`) is a plain ZIP archive. Notes inside are either standalone `<title>.md` files (notes without attachments) or `<title>.textbundle` directories (notes with attachments).
- **The comparison key is the note title** (the file/directory name without its extension). Two notes with the same title are treated as "the same" note — the tool does not compare content or perform any content-level merging.
- **Synchronization is one-round two-way** ("fill missing"): notes that only exist in the source are copied to the destination, and notes that only exist in the destination are copied to the source. Notes present in both archives (`common`) are never modified or compared for content differences.
- **Bear's export may wrap notes in an extra wrapper folder** (e.g. `Bear Notes 2026-08-15 at 00.36.bear2bk/`). The tool automatically descends through single-child wrapper folders until it finds the directory that actually contains the notes.
- **Extraction safety**: the archive is validated (`.bear2bk` extension, valid ZIP) and protected against zip-slip attacks (entries that would resolve outside the destination directory are rejected).
- **Originals are never touched blindly**: before an archive is overwritten, a backup copy (`<file>.bear2bk.bak`) is created next to it.
- The whole operation (extraction, comparison, copying, repacking) happens in temporary directories, and the original `.bear2bk` files are only modified at the very end.

## How it works

The `sync` command:

1. Extracts the `--source` and `--dest` archives into temporary directories.
2. Locates the directory that actually holds the notes in each one (see the wrapper folder note above).
3. Builds the sets of note titles and computes the difference: `only_in_source`, `only_in_dest`, `common`.
4. (optionally) Prints the titles that differ, if `--show-diff` was given.
5. Filters the missing notes using `--include` patterns (if given) and copies:
   - `only_in_source` notes → to `dest`,
   - `only_in_dest` notes → to `source`.
6. If `--dry-run` was given, no files are modified — it only logs what would happen.
7. Otherwise, each modified archive is first backed up (`.bak`), then repacked from the contents of its temporary directory.

The `status` command prints the current sync status as text or JSON (currently always `idle` — a placeholder for future extensions, e.g. remembering the state of the last sync).

## Requirements

- Python 3.10+ (uses `from __future__ import annotations` and `X | None` syntax)
- Dependencies from `requirements.txt` (currently just `pytest`, needed for tests)

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

Running the tool:

```bash
python3 cli.py <command> [options]
```

### `sync` — synchronize two archives

```bash
python3 cli.py sync --source ./backup1.bear2bk --dest ./backup2.bear2bk
```

Options:

| Option | Description |
|---|---|
| `--source PATH` | (required) path to the source `.bear2bk` archive |
| `--dest PATH` | (required) path to the destination `.bear2bk` archive |
| `--workers N` | number of worker threads (default `4`, configurable via `BEARSYNC_WORKERS`) |
| `--dry-run` | show what would happen without touching disk |
| `--include PATTERN` | glob pattern (fnmatch) restricting which notes are copied; can be given multiple times |
| `--show-diff` | list titles of notes that differ between the archives |

Examples:

```bash
# Preview the diff without changing anything on disk
python3 cli.py sync --source ./a.bear2bk --dest ./b.bear2bk --dry-run --show-diff

# Sync only notes matching a pattern
python3 cli.py sync --source ./a.bear2bk --dest ./b.bear2bk --include "Project*"

# Increased log verbosity
python3 cli.py -vv sync --source ./a.bear2bk --dest ./b.bear2bk
```

### `status` — sync status

```bash
python3 cli.py status --format json
```

Options:

| Option | Description |
|---|---|
| `--format {text,json}` | output format (default `text`) |

### Global options

| Option | Description |
|---|---|
| `-v`, `--verbose` | increase log verbosity (repeatable: `-v` = INFO, `-vv` = DEBUG) |
| `-q`, `--quiet` | errors only, suppresses all other logging |
| `-c`, `--config FILE` | path to a config file (defaults from `BEARSYNC_CONFIG`) |
| `--log-file FILE` | also write logs to the given file (defaults from `BEARSYNC_LOG_FILE`) |
| `--version` | print the version and exit |

Environment variables use the `BEARSYNC_` prefix (e.g. `BEARSYNC_WORKERS=8`).

## Tests

```bash
pytest
```

or with a per-file breakdown:

```bash
pytest -v
```

Tests live under `tests/` and cover, among other things: archive extraction/backup (`test_backup.py`), note comparison (`test_compare.py`), merging missing notes (`test_merge.py`), CLI argument validators (`test_validators.py`), and the full command interface (`test_cli.py`, `test_commands.py`).

## Project structure

```
cli.py                    # entry point (runs BearSyncCLI)
bear_sync/
├── cli.py                # builds the argparse parser and dispatches to subcommands
├── commands.py            # logic for the `sync` and `status` commands
├── backup.py              # BearBackupArchive: extract/backup/repack .bear2bk
├── compare.py             # locating notes and comparing titles
├── merge.py                # copying missing notes between archives
├── models.py               # dataclasses: SyncArgs, ArchiveComparison, MergeResult
├── validators.py           # CLI argument validators (paths, archives, numbers)
├── formatting.py            # custom CLI help formatter
├── logging_setup.py         # logging configuration
└── constants.py              # constants: program name, version, env prefix, archive extension
tests/                        # unit tests (pytest)
```
