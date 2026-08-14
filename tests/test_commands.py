from __future__ import annotations

import argparse
import logging

from bear_sync.commands import cmd_status, cmd_sync


def _namespace(source, dest, workers=4, dry_run=False, include=None):
    return argparse.Namespace(
        source=source, dest=dest, workers=workers, dry_run=dry_run, include=include or [],
    )


def test_cmd_sync_logs_note_comparison(make_archive, caplog):
    source = make_archive("source", {"Shared.md": "a", "OnlySource.md": "b"})
    dest = make_archive("dest", {"Shared.md": "a", "OnlyDest.md": "c"})

    with caplog.at_level(logging.DEBUG, logger="bear-sync"):
        exit_code = cmd_sync(_namespace(source, dest))

    assert exit_code == 0
    messages = "\n".join(caplog.messages)
    assert "notes in both archives: 1" in messages
    assert "notes only in source: 1" in messages
    assert "notes only in dest: 1" in messages


def test_cmd_status_text_format(capsys):
    exit_code = cmd_status(argparse.Namespace(format="text"))

    assert exit_code == 0
    assert "status: idle" in capsys.readouterr().out


def test_cmd_status_json_format(capsys):
    exit_code = cmd_status(argparse.Namespace(format="json"))

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == '{"status": "idle"}'
