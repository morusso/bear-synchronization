from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from .constants import BEAR_ARCHIVE_SUFFIX


class BearBackupArchive:
    """A Bear notes ``.bear2bk`` backup, which is a zip archive under the hood.

    Attributes:
        archive_path: Path to the ``.bear2bk`` archive on disk.
    """

    ARCHIVE_SUFFIX = BEAR_ARCHIVE_SUFFIX

    def __init__(self, archive_path: Path) -> None:
        """Initializes the archive wrapper.

        Args:
            archive_path: Path to the ``.bear2bk`` archive on disk.
        """
        self.archive_path = archive_path

    @classmethod
    def extract(cls, archive_path: Path | str, destination: Path | str, *, overwrite: bool = False) -> Path:
        """Extracts a ``.bear2bk`` archive to a destination directory.

        Args:
            archive_path: Path to the ``.bear2bk`` archive to extract.
            destination: Directory the archive contents are extracted into.
            overwrite: Whether to allow extracting into a non-empty destination.

        Returns:
            The destination directory the archive was extracted into.

        Raises:
            FileNotFoundError: If ``archive_path`` does not point to a file.
            ValueError: If the archive has the wrong suffix, is not a valid
                zip file, or contains an unsafe member path.
            FileExistsError: If ``destination`` is non-empty and ``overwrite``
                is ``False``.
        """
        archive = cls(Path(archive_path))
        return archive._extract_to(Path(destination), overwrite=overwrite)

    @classmethod
    def backup(cls, archive_path: Path | str) -> Path:
        """Copies ``archive_path`` to a sibling ``.bak`` file.

        Args:
            archive_path: Path to the archive to back up.

        Returns:
            The path of the newly created ``.bak`` copy.
        """
        archive_path = Path(archive_path)
        backup_path = archive_path.with_name(archive_path.name + ".bak")
        shutil.copy2(archive_path, backup_path)
        return backup_path

    @classmethod
    def repack(cls, source_dir: Path | str, archive_path: Path | str) -> Path:
        """Rewrites ``archive_path`` from the contents of ``source_dir``.

        Args:
            source_dir: Directory whose files are written into the archive.
            archive_path: Path of the archive to rewrite.

        Returns:
            The path of the rewritten archive.
        """
        source_dir = Path(source_dir)
        archive_path = Path(archive_path)
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source_dir.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(source_dir))
        return archive_path

    def _extract_to(self, destination: Path, *, overwrite: bool) -> Path:
        """Validates the archive and extracts it into ``destination``.

        Args:
            destination: Directory the archive contents are extracted into.
            overwrite: Whether to allow extracting into a non-empty destination.

        Returns:
            The destination directory the archive was extracted into.

        Raises:
            FileExistsError: If ``destination`` is non-empty and ``overwrite``
                is ``False``.
        """
        self._validate_archive()

        if destination.exists() and any(destination.iterdir()) and not overwrite:
            raise FileExistsError(f"destination is not empty: {destination}")
        destination.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.archive_path) as archive:
            self._extract_safely(archive, destination)

        return destination

    def _validate_archive(self) -> None:
        """Validates that the archive exists, has the right suffix, and is a zip.

        Raises:
            FileNotFoundError: If ``self.archive_path`` does not point to a file.
            ValueError: If the suffix is wrong or the file is not a valid zip.
        """
        if not self.archive_path.is_file():
            raise FileNotFoundError(f"archive not found: {self.archive_path}")
        if self.archive_path.suffix != self.ARCHIVE_SUFFIX:
            raise ValueError(f"expected a {self.ARCHIVE_SUFFIX} archive, got: {self.archive_path.name}")
        if not zipfile.is_zipfile(self.archive_path):
            raise ValueError(f"not a valid zip archive: {self.archive_path}")

    @staticmethod
    def _extract_safely(archive: zipfile.ZipFile, destination: Path) -> None:
        """Extracts a zip archive after guarding against path traversal (zip slip).

        Args:
            archive: Open zip archive to extract.
            destination: Directory the archive contents are extracted into.

        Raises:
            ValueError: If any archive member would resolve outside of
                ``destination``.
        """
        destination_root = destination.resolve()
        for member in archive.infolist():
            resolved = (destination / member.filename).resolve()
            if resolved != destination_root and destination_root not in resolved.parents:
                raise ValueError(f"unsafe path in archive: {member.filename}")
        archive.extractall(destination)
