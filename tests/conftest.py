from __future__ import annotations

import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def make_archive(tmp_path):
    """Build a .bear2bk zip archive from {relative_path: content} entries."""

    def _make(name: str, entries: dict[str, str], *, suffix: str = ".bear2bk") -> Path:
        archive_path = tmp_path / f"{name}{suffix}"
        with zipfile.ZipFile(archive_path, "w") as zf:
            for rel_path, content in entries.items():
                zf.writestr(rel_path, content)
        return archive_path

    return _make
