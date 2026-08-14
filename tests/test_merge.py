from __future__ import annotations

from pathlib import Path

from bear_sync.compare import compare_archives, list_notes
from bear_sync.merge import fill_missing_notes


def _touch(path: Path) -> None:
    """Creates ``path`` and its parent directories, writing placeholder content.

    Args:
        path: File path to create.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("content")


def test_fill_missing_notes_copies_plain_markdown_both_ways(tmp_path):
    """``fill_missing_notes`` copies plain markdown notes in both directions."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Shared.md")
    _touch(source / "OnlySource.md")
    _touch(dest / "Shared.md")
    _touch(dest / "OnlyDest.md")
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison)

    assert result.added_to_dest == {"OnlySource"}
    assert result.added_to_source == {"OnlyDest"}
    assert (dest / "OnlySource.md").exists()
    assert (source / "OnlyDest.md").exists()


def test_fill_missing_notes_copies_textbundle_directories(tmp_path):
    """``fill_missing_notes`` copies textbundle directories along with their attachments."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "WithAttachment.textbundle" / "text.md")
    _touch(source / "WithAttachment.textbundle" / "assets" / "image.png")
    dest.mkdir()
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison)

    assert result.added_to_dest == {"WithAttachment"}
    assert (dest / "WithAttachment.textbundle" / "text.md").read_text() == "content"
    assert (dest / "WithAttachment.textbundle" / "assets" / "image.png").exists()


def test_fill_missing_notes_dry_run_does_not_touch_disk(tmp_path):
    """``fill_missing_notes`` with ``dry_run=True`` reports the diff but copies nothing."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "OnlySource.md")
    dest.mkdir()
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison, dry_run=True)

    assert result.added_to_dest == {"OnlySource"}
    assert not (dest / "OnlySource.md").exists()
    assert list_notes(dest) == {}


def test_fill_missing_notes_respects_include_filter(tmp_path):
    """``fill_missing_notes`` only copies notes matching the ``include`` patterns."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Keep This.md")
    _touch(source / "Skip This.md")
    dest.mkdir()
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison, include=["Keep*"])

    assert result.added_to_dest == {"Keep This"}
    assert (dest / "Keep This.md").exists()
    assert not (dest / "Skip This.md").exists()


def test_fill_missing_notes_places_copies_inside_export_wrapper_folder(tmp_path):
    """``fill_missing_notes`` places copied notes inside the destination's own wrapper folder."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Bear Notes 2026-08-15 at 00.36.bear2bk" / "New Note.textbundle" / "text.md")
    _touch(dest / "Bear Notes 2026-01-01 at 09.00.bear2bk" / "Existing.textbundle" / "text.md")
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison)

    assert result.added_to_dest == {"New Note"}
    copied = dest / "Bear Notes 2026-01-01 at 09.00.bear2bk" / "New Note.textbundle" / "text.md"
    assert copied.read_text() == "content"


def test_fill_missing_notes_no_diff_is_a_noop(tmp_path):
    """``fill_missing_notes`` copies nothing when both archives already match."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Shared.md")
    _touch(dest / "Shared.md")
    comparison = compare_archives(source, dest)

    result = fill_missing_notes(source, dest, comparison)

    assert result.added_to_dest == set()
    assert result.added_to_source == set()
