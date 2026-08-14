from __future__ import annotations

import zipfile
import pytest
from bear_sync.backup import BearBackupArchive


def test_extract_creates_destination_and_writes_files(tmp_path, make_archive):
    """Extracting an archive creates the destination and writes its files."""
    archive = make_archive("backup", {"Note.md": "hello"})
    dest = tmp_path / "out"

    result = BearBackupArchive.extract(archive, dest)

    assert result == dest
    assert (dest / "Note.md").read_text() == "hello"


def test_extract_missing_archive_raises(tmp_path):
    """Extracting a non-existent archive raises ``FileNotFoundError``."""
    with pytest.raises(FileNotFoundError):
        BearBackupArchive.extract(tmp_path / "missing.bear2bk", tmp_path / "out")


def test_extract_wrong_suffix_raises(tmp_path):
    """Extracting an archive with the wrong file suffix raises ``ValueError``."""
    bad = tmp_path / "backup.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("Note.md", "hello")

    with pytest.raises(ValueError, match=r"expected a \.bear2bk archive"):
        BearBackupArchive.extract(bad, tmp_path / "out")


def test_extract_invalid_zip_raises(tmp_path):
    """Extracting a file that is not a valid zip archive raises ``ValueError``."""
    bad = tmp_path / "backup.bear2bk"
    bad.write_text("not a zip")

    with pytest.raises(ValueError, match="not a valid zip archive"):
        BearBackupArchive.extract(bad, tmp_path / "out")


def test_extract_refuses_nonempty_destination_without_overwrite(tmp_path, make_archive):
    """Extracting into a non-empty destination without ``overwrite`` raises."""
    archive = make_archive("backup", {"Note.md": "hello"})
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "existing.txt").write_text("keep me")

    with pytest.raises(FileExistsError):
        BearBackupArchive.extract(archive, dest)


def test_extract_overwrite_true_allows_nonempty_destination(tmp_path, make_archive):
    """Extracting with ``overwrite=True`` allows a non-empty destination and preserves its files."""
    archive = make_archive("backup", {"Note.md": "hello"})
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "existing.txt").write_text("keep me")

    result = BearBackupArchive.extract(archive, dest, overwrite=True)

    assert (result / "Note.md").exists()
    assert (result / "existing.txt").exists()


def test_extract_rejects_zip_slip(tmp_path):
    """Extracting an archive with a path-traversal member raises ``ValueError``."""
    malicious = tmp_path / "backup.bear2bk"
    with zipfile.ZipFile(malicious, "w") as zf:
        zf.writestr("../../evil.txt", "pwned")

    with pytest.raises(ValueError, match="unsafe path in archive"):
        BearBackupArchive.extract(malicious, tmp_path / "out")


def test_backup_creates_bak_copy_alongside_original(tmp_path, make_archive):
    """Backing up an archive creates a byte-identical sibling ``.bak`` file."""
    archive = make_archive("backup", {"Note.md": "hello"})

    backup_path = BearBackupArchive.backup(archive)

    assert backup_path == archive.with_name(archive.name + ".bak")
    assert backup_path.read_bytes() == archive.read_bytes()


def test_repack_rewrites_archive_from_directory_contents(tmp_path, make_archive):
    """Repacking rewrites the archive so it reflects the source directory's current contents."""
    archive = make_archive("backup", {"Old.md": "stale"})
    source_dir = tmp_path / "extracted"
    (source_dir / "New.md").parent.mkdir(parents=True, exist_ok=True)
    (source_dir / "New.md").write_text("fresh")

    result = BearBackupArchive.repack(source_dir, archive)

    assert result == archive
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    assert names == ["New.md"]
    extracted = BearBackupArchive.extract(archive, tmp_path / "out")
    assert (extracted / "New.md").read_text() == "fresh"
