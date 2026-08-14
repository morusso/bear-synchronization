from __future__ import annotations

import argparse

import pytest

from bear_sync.validators import existing_bear2bk_archive, existing_path, positive_int


def test_existing_path_returns_path_for_existing_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("x")

    assert existing_path(str(file)) == file


def test_existing_path_raises_for_missing_path(tmp_path):
    with pytest.raises(argparse.ArgumentTypeError):
        existing_path(str(tmp_path / "missing.txt"))


def test_existing_bear2bk_archive_accepts_existing_bear2bk_file(tmp_path):
    file = tmp_path / "backup.bear2bk"
    file.write_text("")

    assert existing_bear2bk_archive(str(file)) == file


def test_existing_bear2bk_archive_rejects_wrong_suffix(tmp_path):
    file = tmp_path / "backup.zip"
    file.write_text("")

    with pytest.raises(argparse.ArgumentTypeError, match=r"\.bear2bk"):
        existing_bear2bk_archive(str(file))


def test_existing_bear2bk_archive_rejects_missing_file(tmp_path):
    with pytest.raises(argparse.ArgumentTypeError, match="does not exist"):
        existing_bear2bk_archive(str(tmp_path / "missing.bear2bk"))


@pytest.mark.parametrize("value", ["1", "42", "1000"])
def test_positive_int_accepts_positive_values(value):
    assert positive_int(value) == int(value)


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_positive_int_rejects_non_positive_or_non_numeric(value):
    with pytest.raises(argparse.ArgumentTypeError):
        positive_int(value)
