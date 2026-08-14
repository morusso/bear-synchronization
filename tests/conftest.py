from __future__ import annotations

import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def make_archive(tmp_path):
    """Provides a factory for building ``.bear2bk`` zip archives in ``tmp_path``.

    Returns:
        A callable that builds an archive from ``{relative_path: content}``
        entries and returns its path.
    """

    def _make(name: str, entries: dict[str, str], *, suffix: str = ".bear2bk") -> Path:
        """Builds a zip archive from ``{relative_path: content}`` entries.

        Args:
            name: Base name of the archive file, without suffix.
            entries: Mapping of relative path (inside the archive) to its
                text content.
            suffix: File suffix to use for the archive.

        Returns:
            The path of the created archive.
        """
        archive_path = tmp_path / f"{name}{suffix}"
        with zipfile.ZipFile(archive_path, "w") as zf:
            for rel_path, content in entries.items():
                zf.writestr(rel_path, content)
        return archive_path

    return _make
