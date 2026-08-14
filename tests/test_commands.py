from __future__ import annotations

import argparse
import logging

from bear_sync.backup import BearBackupArchive
from bear_sync.commands import cmd_status, cmd_sync


def _namespace(source, dest, workers=4, dry_run=False, include=None, show_diff=False):
    return argparse.Namespace(
        source=source, dest=dest, workers=workers, dry_run=dry_run,
        include=include or [], show_diff=show_diff,
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


def test_cmd_sync_show_diff_prints_differing_titles(make_archive, capsys):
    source = make_archive("source", {"Shared.md": "a", "OnlySource.md": "b"})
    dest = make_archive("dest", {"Shared.md": "a", "OnlyDest.md": "c"})

    exit_code = cmd_sync(_namespace(source, dest, show_diff=True))

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Only in source (1):" in out
    assert "- OnlySource" in out
    assert "Only in dest (1):" in out
    assert "- OnlyDest" in out
    assert "Shared" not in out


def test_cmd_sync_without_show_diff_prints_nothing(make_archive, capsys):
    source = make_archive("source", {"Shared.md": "a", "OnlySource.md": "b"})
    dest = make_archive("dest", {"Shared.md": "a", "OnlyDest.md": "c"})

    cmd_sync(_namespace(source, dest, show_diff=False))

    assert capsys.readouterr().out == ""


def test_cmd_sync_fills_missing_notes_into_both_archives(tmp_path, make_archive):
    source = make_archive("source", {"Shared.md": "a", "OnlySource.md": "b"})
    dest = make_archive("dest", {"Shared.md": "a", "OnlyDest.md": "c"})

    exit_code = cmd_sync(_namespace(source, dest))

    assert exit_code == 0
    source_out = BearBackupArchive.extract(source, tmp_path / "source_check")
    dest_out = BearBackupArchive.extract(dest, tmp_path / "dest_check")
    assert {p.name for p in source_out.iterdir()} == {"Shared.md", "OnlySource.md", "OnlyDest.md"}
    assert {p.name for p in dest_out.iterdir()} == {"Shared.md", "OnlyDest.md", "OnlySource.md"}
    assert (dest_out / "OnlySource.md").read_text() == "b"
    assert (source_out / "OnlyDest.md").read_text() == "c"


def test_cmd_sync_creates_bak_files_before_overwriting(tmp_path, make_archive):
    source = make_archive("source", {"OnlySource.md": "b"})
    dest = make_archive("dest", {"OnlyDest.md": "c"})

    cmd_sync(_namespace(source, dest))

    assert source.with_name(source.name + ".bak").exists()
    assert dest.with_name(dest.name + ".bak").exists()


def test_cmd_sync_dry_run_does_not_modify_archives(tmp_path, make_archive):
    source = make_archive("source", {"OnlySource.md": "b"})
    dest = make_archive("dest", {"OnlyDest.md": "c"})
    source_bytes_before = source.read_bytes()
    dest_bytes_before = dest.read_bytes()

    exit_code = cmd_sync(_namespace(source, dest, dry_run=True))

    assert exit_code == 0
    assert source.read_bytes() == source_bytes_before
    assert dest.read_bytes() == dest_bytes_before
    assert not source.with_name(source.name + ".bak").exists()
    assert not dest.with_name(dest.name + ".bak").exists()


def test_cmd_sync_include_filter_limits_which_notes_are_filled(tmp_path, make_archive):
    source = make_archive("source", {"Keep This.md": "a", "Skip This.md": "b"})
    dest = make_archive("dest", {})

    cmd_sync(_namespace(source, dest, include=["Keep*"]))

    dest_out = BearBackupArchive.extract(dest, tmp_path / "dest_check")
    assert {p.name for p in dest_out.iterdir()} == {"Keep This.md"}


def test_cmd_sync_already_in_sync_does_not_touch_archives(make_archive):
    source = make_archive("source", {"Shared.md": "a"})
    dest = make_archive("dest", {"Shared.md": "a"})
    source_bytes_before = source.read_bytes()
    dest_bytes_before = dest.read_bytes()

    exit_code = cmd_sync(_namespace(source, dest))

    assert exit_code == 0
    assert source.read_bytes() == source_bytes_before
    assert dest.read_bytes() == dest_bytes_before
    assert not source.with_name(source.name + ".bak").exists()
    assert not dest.with_name(dest.name + ".bak").exists()


def test_cmd_status_text_format(capsys):
    exit_code = cmd_status(argparse.Namespace(format="text"))

    assert exit_code == 0
    assert "status: idle" in capsys.readouterr().out


def test_cmd_status_json_format(capsys):
    exit_code = cmd_status(argparse.Namespace(format="json"))

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == '{"status": "idle"}'
