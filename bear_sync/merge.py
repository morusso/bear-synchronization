from __future__ import annotations

import fnmatch
import logging
import shutil
from pathlib import Path

from .compare import list_notes, notes_container
from .constants import PROG_NAME
from .models import ArchiveComparison, MergeResult

logger = logging.getLogger(PROG_NAME)


def _matching(titles: set[str], include: list[str]) -> set[str]:
    """Filters titles down to those matching at least one include pattern.

    Args:
        titles: Candidate note titles.
        include: Glob-style patterns (per ``fnmatch``) to match against. If
            empty, all titles are kept.

    Returns:
        The subset of ``titles`` matching ``include``, or all of ``titles``
        if ``include`` is empty.
    """
    if not include:
        return set(titles)
    return {title for title in titles if any(fnmatch.fnmatch(title, pattern) for pattern in include)}


def _copy_note(note_path: Path, destination_root: Path) -> None:
    """Copies a single note (file or textbundle directory) into a destination.

    Args:
        note_path: Path to the note file or textbundle directory to copy.
        destination_root: Directory the note is copied into.
    """
    target = destination_root / note_path.name
    if note_path.is_dir():
        shutil.copytree(note_path, target)
    else:
        shutil.copy2(note_path, target)


def fill_missing_notes(
    source_root: Path,
    dest_root: Path,
    comparison: ArchiveComparison,
    *,
    include: list[str] | None = None,
    dry_run: bool = False,
) -> MergeResult:
    """Copies notes missing on one side into the other extracted archive tree.

    Args:
        source_root: Root of the extracted source archive.
        dest_root: Root of the extracted destination archive.
        comparison: Result of comparing the two archives' note titles.
        include: Glob-style patterns restricting which notes are copied. If
            empty or ``None``, all missing notes are copied.
        dry_run: If ``True``, only determine which notes would be copied
            without touching disk.

    Returns:
        A ``MergeResult`` with the titles actually selected for copying
        (after ``include`` filtering); with ``dry_run`` the trees are left
        untouched.
    """
    include = include or []
    source_notes = list_notes(source_root)
    dest_notes = list_notes(dest_root)
    source_container = notes_container(source_root)
    dest_container = notes_container(dest_root)

    to_dest = _matching(comparison.only_in_source, include)
    to_source = _matching(comparison.only_in_dest, include)

    for title in sorted(to_dest):
        logger.info("copying note %r: source -> dest", title)
        if not dry_run:
            _copy_note(source_notes[title], dest_container)

    for title in sorted(to_source):
        logger.info("copying note %r: dest -> source", title)
        if not dry_run:
            _copy_note(dest_notes[title], source_container)

    return MergeResult(added_to_source=to_source, added_to_dest=to_dest)
