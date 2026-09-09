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


def test_ebook_metadata_null_and_missing_description(tmp_path: Path) -> None:
    # 1. Test null description in JSON payload
    null_json = '{"title": "Test Book", "author": "Author", "description": null}'
    p1 = tmp_path / "null_meta.json"
    p1.write_text(null_json, encoding="utf-8")
    loaded1 = EbookMetadata.load_from_file(p1)
    assert loaded1.description == ""

    # 2. Test missing description field in JSON payload
    missing_json = '{"title": "Test Book 2", "author": "Author 2"}'
    p2 = tmp_path / "missing_meta.json"
    p2.write_text(missing_json, encoding="utf-8")
    loaded2 = EbookMetadata.load_from_file(p2)
    assert loaded2.description == ""

    # 3. Direct instantiation with None
    meta3 = EbookMetadata(title="Test Book 3", author="Author 3", description=None)
    assert meta3.description == ""


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
    settings.kindle_email = "reader@kindle.com"
    settings.smtp_user = "author@gmail.com"
    settings.smtp_password = "app-password"
    settings.save_to_file(settings_path)

    loaded = AppSettings.load_from_file(settings_path)
    assert loaded.recent_ebooks == settings.recent_ebooks
    assert loaded.theme == "dark"
    assert loaded.kindle_email == "reader@kindle.com"
    assert loaded.smtp_user == "author@gmail.com"
    assert loaded.smtp_password == "app-password"
    assert loaded.smtp_server == "smtp.gmail.com"
    assert loaded.smtp_port == 587


def test_ebook_metadata_finished_flag(tmp_path: Path) -> None:
    meta = EbookMetadata(
        title="Finished Book",
        author="Author",
        finished=True,
    )
    p = tmp_path / "meta_finished.json"
    meta.save_to_file(p)

    loaded = EbookMetadata.load_from_file(p)
    assert loaded.finished is True


def test_app_settings_prune_invalid_recents(tmp_path: Path) -> None:
    settings = AppSettings()
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()
    (valid_dir / "metadata.json").write_text("{}", encoding="utf-8")

    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()

    missing_dir = tmp_path / "missing"

    settings.add_recent_ebook(str(valid_dir))
    settings.add_recent_ebook(str(invalid_dir))
    settings.add_recent_ebook(str(missing_dir))

    assert len(settings.recent_ebooks) == 3
    changed = settings.prune_invalid_recents()
    assert changed is True
    assert settings.recent_ebooks == [str(valid_dir.resolve())]
    assert settings.last_opened_ebook == str(valid_dir.resolve())

    # Second call with nothing to prune returns False
    assert settings.prune_invalid_recents() is False


    # Default should be False
    default_meta = EbookMetadata(title="Draft Book", author="Author")
    assert default_meta.finished is False
