from __future__ import annotations

import zipfile
from pathlib import Path

from .constants import BEAR_ARCHIVE_SUFFIX


class BearBackupArchive:
    """A Bear notes ``.bear2bk`` backup, which is a zip archive under the hood."""

    ARCHIVE_SUFFIX = BEAR_ARCHIVE_SUFFIX

    def __init__(self, archive_path: Path) -> None:
        self.archive_path = archive_path

    @classmethod
    def extract(cls, archive_path: Path | str, destination: Path | str, *, overwrite: bool = False) -> Path:
        archive = cls(Path(archive_path))
        return archive._extract_to(Path(destination), overwrite=overwrite)

    def _extract_to(self, destination: Path, *, overwrite: bool) -> Path:
        self._validate_archive()

        if destination.exists() and any(destination.iterdir()) and not overwrite:
            raise FileExistsError(f"destination is not empty: {destination}")
        destination.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.archive_path) as archive:
            self._extract_safely(archive, destination)

        return destination

    def _validate_archive(self) -> None:
        if not self.archive_path.is_file():
            raise FileNotFoundError(f"archive not found: {self.archive_path}")
        if self.archive_path.suffix != self.ARCHIVE_SUFFIX:
            raise ValueError(f"expected a {self.ARCHIVE_SUFFIX} archive, got: {self.archive_path.name}")
        if not zipfile.is_zipfile(self.archive_path):
            raise ValueError(f"not a valid zip archive: {self.archive_path}")

    @staticmethod
    def _extract_safely(archive: zipfile.ZipFile, destination: Path) -> None:
        destination_root = destination.resolve()
        for member in archive.infolist():
            resolved = (destination / member.filename).resolve()
            if resolved != destination_root and destination_root not in resolved.parents:
                raise ValueError(f"unsafe path in archive: {member.filename}")
        archive.extractall(destination)
