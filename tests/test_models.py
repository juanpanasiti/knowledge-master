"""Unit tests for EbookMetadata and AppSettings models."""

from pathlib import Path
from ebook_editor.core.models import EbookMetadata, AppSettings


def test_ebook_metadata_serialization(tmp_path: Path) -> None:
    meta = EbookMetadata(
        title="OpenSpec Guide",
        author="Alice Developer",
        description="Comprehensive guide to OpenSpec",
        tags=["openspec", "python"],
    )
    meta_path = tmp_path / "metadata.json"
    meta.save_to_file(meta_path)

    loaded = EbookMetadata.load_from_file(meta_path)
    assert loaded.title == "OpenSpec Guide"
    assert loaded.author == "Alice Developer"
    assert loaded.cover_path == "assets/cover.png"
    assert loaded.tags == ["openspec", "python"]
    assert loaded.created_at is not None
    assert loaded.updated_at is not None


def test_app_settings_recent_ebooks(tmp_path: Path) -> None:
    settings = AppSettings()
    book1 = str(tmp_path / "book1")
    book2 = str(tmp_path / "book2")

    settings.add_recent_ebook(book1)
    assert settings.recent_ebooks == [str(Path(book1).resolve())]
    assert settings.last_opened_ebook == str(Path(book1).resolve())

    settings.add_recent_ebook(book2)
    assert settings.recent_ebooks[0] == str(Path(book2).resolve())
    assert settings.last_opened_ebook == str(Path(book2).resolve())

    # Re-adding book1 moves it to the top
    settings.add_recent_ebook(book1)
    assert settings.recent_ebooks[0] == str(Path(book1).resolve())

    settings_path = tmp_path / "config.json"
    settings.save_to_file(settings_path)

    loaded = AppSettings.load_from_file(settings_path)
    assert loaded.recent_ebooks == settings.recent_ebooks
    assert loaded.theme == "dark"
