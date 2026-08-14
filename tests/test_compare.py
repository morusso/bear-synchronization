from __future__ import annotations

from pathlib import Path

from bear_sync.compare import compare_archives, list_notes, note_titles, notes_container


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("content")


def test_note_titles_finds_textbundles_and_plain_markdown(tmp_path):
    _touch(tmp_path / "With Attachment.textbundle" / "text.md")
    _touch(tmp_path / "With Attachment.textbundle" / "assets" / "image.png")
    _touch(tmp_path / "Plain Note.md")

    assert note_titles(tmp_path) == {"With Attachment", "Plain Note"}


def test_note_titles_ignores_md_files_inside_textbundles(tmp_path):
    _touch(tmp_path / "Bundle.textbundle" / "text.md")

    assert note_titles(tmp_path) == {"Bundle"}


def test_note_titles_empty_directory_returns_empty_set(tmp_path):
    assert note_titles(tmp_path) == set()


def test_compare_archives_reports_common_and_unique_notes(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Shared.md")
    _touch(source / "Only Source.md")
    _touch(dest / "Shared.md")
    _touch(dest / "Only Dest.md")

    result = compare_archives(source, dest)

    assert result.common == {"Shared"}
    assert result.only_in_source == {"Only Source"}
    assert result.only_in_dest == {"Only Dest"}


def test_notes_container_descends_through_export_wrapper_folder(tmp_path):
    wrapper = tmp_path / "Bear Notes 2026-08-15 at 00.36.bear2bk"
    _touch(wrapper / "Some Note.textbundle" / "text.md")

    assert notes_container(tmp_path) == wrapper
    assert list_notes(tmp_path) == {"Some Note": wrapper / "Some Note.textbundle"}


def test_compare_archives_handles_differently_named_wrapper_folders(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Bear Notes 2026-08-15 at 00.36.bear2bk" / "Shared.textbundle" / "text.md")
    _touch(source / "Bear Notes 2026-08-15 at 00.36.bear2bk" / "Only Source.textbundle" / "text.md")
    _touch(dest / "Bear Notes 2026-01-01 at 09.00.bear2bk" / "Shared.textbundle" / "text.md")
    _touch(dest / "Bear Notes 2026-01-01 at 09.00.bear2bk" / "Only Dest.textbundle" / "text.md")

    result = compare_archives(source, dest)

    assert result.common == {"Shared"}
    assert result.only_in_source == {"Only Source"}
    assert result.only_in_dest == {"Only Dest"}


def test_compare_archives_identical_note_sets(tmp_path):
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    _touch(source / "Shared.md")
    _touch(dest / "Shared.md")

    result = compare_archives(source, dest)

    assert result.common == {"Shared"}
    assert result.only_in_source == set()
    assert result.only_in_dest == set()
