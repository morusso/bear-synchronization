from __future__ import annotations

from pathlib import Path

from .models import ArchiveComparison


def note_titles(root: Path) -> set[str]:
    """Collect note titles from an extracted .bear2bk backup directory.

    Notes with attachments are exported as ``<title>.textbundle`` directories;
    plain notes are exported as standalone ``<title>.md`` files.
    """
    titles: set[str] = set()
    for bundle in root.rglob("*.textbundle"):
        titles.add(bundle.stem)
    for note in root.rglob("*.md"):
        if any(parent.suffix == ".textbundle" for parent in note.parents):
            continue
        titles.add(note.stem)
    return titles


def compare_archives(source_root: Path, dest_root: Path) -> ArchiveComparison:
    source_titles = note_titles(source_root)
    dest_titles = note_titles(dest_root)
    return ArchiveComparison(
        common=source_titles & dest_titles,
        only_in_source=source_titles - dest_titles,
        only_in_dest=dest_titles - source_titles,
    )
