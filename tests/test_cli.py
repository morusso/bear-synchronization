from __future__ import annotations

import zipfile

import pytest

from bear_sync.cli import BearSyncCLI


def test_version_flag_exits_zero(capsys):
    cli = BearSyncCLI()

    with pytest.raises(SystemExit) as exc_info:
        cli.run(["--version"])

    assert exc_info.value.code == 0
    assert "bear-sync" in capsys.readouterr().out


def test_missing_required_command_exits_nonzero():
    cli = BearSyncCLI()

    with pytest.raises(SystemExit):
        cli.run([])


def test_sync_rejects_source_with_wrong_suffix(tmp_path, capsys):
    bad_source = tmp_path / "source.zip"
    bad_source.write_text("")
    dest = tmp_path / "dest.bear2bk"
    dest.write_text("")

    cli = BearSyncCLI()
    with pytest.raises(SystemExit) as exc_info:
        cli.run(["sync", "--source", str(bad_source), "--dest", str(dest)])

    assert exc_info.value.code == 2
    assert ".bear2bk" in capsys.readouterr().err


def test_sync_end_to_end_returns_zero(make_archive):
    source = make_archive("source", {"Note.md": "hello"})
    dest = make_archive("dest", {"Note.md": "hello"})

    cli = BearSyncCLI()
    exit_code = cli.run(["sync", "--source", str(source), "--dest", str(dest)])

    assert exit_code == 0


def test_sync_extraction_failure_is_caught_and_returns_one(tmp_path):
    corrupt_source = tmp_path / "source.bear2bk"
    corrupt_source.write_text("not a zip")
    dest = tmp_path / "dest.bear2bk"
    with zipfile.ZipFile(dest, "w"):
        pass

    cli = BearSyncCLI()
    exit_code = cli.run(["sync", "--source", str(corrupt_source), "--dest", str(dest)])

    assert exit_code == 1


def test_status_json_output(capsys):
    cli = BearSyncCLI()
    exit_code = cli.run(["status", "--format", "json"])

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == '{"status": "idle"}'
