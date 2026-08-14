from __future__ import annotations

from pathlib import Path

from .models import ArchiveComparison


def _is_note(entry: Path) -> bool:
    """Checks whether a directory entry is a Bear note bundle.

    Args:
        entry: Directory entry to check.

    Returns:
        ``True`` if ``entry`` is a ``.textbundle`` directory or a ``.md`` file.
    """
    return (entry.is_dir() and entry.suffix == ".textbundle") or (entry.is_file() and entry.suffix == ".md")


def notes_container(root: Path) -> Path:
    """Locates the directory that directly holds note bundles.

    A .bear2bk export wraps its notes in a single top-level folder named
    after the backup (e.g. ``Bear Notes 2026-08-15 at 00.36.bear2bk/``), so
    descend through single-child wrapper directories until note bundles
    are found (or there is nowhere left to descend into).

    Args:
        root: Directory to search, typically the root of an extracted
            ``.bear2bk`` archive.

    Returns:
        The directory that directly contains note bundles.
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
    """Maps note title to its path in an extracted .bear2bk backup.

    Notes with attachments are exported as ``<title>.textbundle`` directories;
    plain notes are exported as standalone ``<title>.md`` files.

    Args:
        root: Directory to search, typically the root of an extracted
            ``.bear2bk`` archive.

    Returns:
        A mapping of note title to its path.
    """
    notes: dict[str, Path] = {}
    for entry in notes_container(root).iterdir():
        if _is_note(entry):
            notes[entry.stem] = entry
    return notes


def note_titles(root: Path) -> set[str]:
    """Lists the titles of all notes found under a directory.

    Args:
        root: Directory to search, typically the root of an extracted
            ``.bear2bk`` archive.

    Returns:
        The set of note titles found.
    """
    return set(list_notes(root))


def compare_archives(source_root: Path, dest_root: Path) -> ArchiveComparison:
    """Compares the note titles present in two extracted archives.

    Args:
        source_root: Root of the extracted source archive.
        dest_root: Root of the extracted destination archive.

    Returns:
        An ``ArchiveComparison`` with the common and unique note titles.
    """
    source_titles = note_titles(source_root)
    dest_titles = note_titles(dest_root)
    return ArchiveComparison(
        common=source_titles & dest_titles,
        only_in_source=source_titles - dest_titles,
        only_in_dest=dest_titles - source_titles,
    )
