from __future__ import annotations

from pathlib import Path

from .models import ArchiveComparison


def _is_note(entry: Path) -> bool:
    return (entry.is_dir() and entry.suffix == ".textbundle") or (entry.is_file() and entry.suffix == ".md")


def notes_container(root: Path) -> Path:
    """Locate the directory that directly holds note bundles.

    A .bear2bk export wraps its notes in a single top-level folder named
    after the backup (e.g. ``Bear Notes 2026-08-15 at 00.36.bear2bk/``), so
    descend through single-child wrapper directories until note bundles
    are found (or there is nowhere left to descend into).
    """
    current = root
    while True:
        children = list(current.iterdir())
        if any(_is_note(child) for child in children):
            return current
        if len(children) != 1 or not children[0].is_dir():
            return current
        current = children[0]


def list_notes(root: Path) -> dict[str, Path]:
    """Map note title -> its path in an extracted .bear2bk backup.

    Notes with attachments are exported as ``<title>.textbundle`` directories;
    plain notes are exported as standalone ``<title>.md`` files.
    """
    notes: dict[str, Path] = {}
    for entry in notes_container(root).iterdir():
        if _is_note(entry):
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
