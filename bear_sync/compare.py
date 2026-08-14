from __future__ import annotations

from pathlib import Path

from .models import ArchiveComparison


def list_notes(root: Path) -> dict[str, Path]:
    """Map note title -> its top-level path in an extracted .bear2bk backup.

    Notes with attachments are exported as ``<title>.textbundle`` directories;
    plain notes are exported as standalone ``<title>.md`` files.
    """
    notes: dict[str, Path] = {}
    for entry in root.iterdir():
        if entry.is_dir() and entry.suffix == ".textbundle":
            notes[entry.stem] = entry
        elif entry.is_file() and entry.suffix == ".md":
            notes[entry.stem] = entry
    return notes


def note_titles(root: Path) -> set[str]:
    return set(list_notes(root))


def compare_archives(source_root: Path, dest_root: Path) -> ArchiveComparison:
    source_titles = note_titles(source_root)
    dest_titles = note_titles(dest_root)
    return ArchiveComparison(
        common=source_titles & dest_titles,
        only_in_source=source_titles - dest_titles,
        only_in_dest=dest_titles - source_titles,
    )
