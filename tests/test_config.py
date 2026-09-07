"""Unit tests for ConfigManager."""

from pathlib import Path
from ebook_editor.core.config import ConfigManager


def test_config_manager_initialization(tmp_path: Path) -> None:
    root = tmp_path / "test-km"
    manager = ConfigManager(root_dir=root)
    assert not root.exists()

    settings = manager.load_settings()
    assert root.exists()
    assert (root / "ebooks").exists()
    assert (root / "config.json").exists()
    assert settings.theme == "dark"
    assert settings.cover_size == "medium"


def test_config_manager_recent_ebooks(tmp_path: Path) -> None:
    root = tmp_path / "test-km"
    manager = ConfigManager(root_dir=root)

    ebook_path = tmp_path / "my-book"
    settings = manager.add_recent_ebook(ebook_path)
    assert str(ebook_path.resolve()) in settings.recent_ebooks

    manager.set_theme("light")
    reloaded = manager.load_settings()
    assert reloaded.theme == "light"
    assert str(ebook_path.resolve()) in reloaded.recent_ebooks

    manager.remove_recent_ebook(ebook_path)
    reloaded_after_removal = manager.load_settings()
    assert str(ebook_path.resolve()) not in reloaded_after_removal.recent_ebooks


def test_config_manager_cover_size_persistence(tmp_path: Path) -> None:
    root = tmp_path / "test-km"
    manager = ConfigManager(root_dir=root)

    settings = manager.load_settings()
    assert settings.cover_size == "medium"

    manager.set_cover_size("large")
    reloaded = manager.load_settings()
    assert reloaded.cover_size == "large"

    manager.set_cover_size("small")
    reloaded_small = manager.load_settings()
    assert reloaded_small.cover_size == "small"


def test_config_manager_explorer_expanded_sections(tmp_path: Path) -> None:
    root = tmp_path / "test-km"
    manager = ConfigManager(root_dir=root)

    # Default fallback
    assert manager.get_explorer_expanded_sections("book-1") == ["content", "resources"]

    # Persist custom state
    manager.set_explorer_expanded_sections("book-1", ["content", "assets", "dist"])
    reloaded = manager.load_settings()
    assert reloaded.get_explorer_expanded_sections("book-1") == ["content", "assets", "dist"]
    assert manager.get_explorer_expanded_sections("book-1") == ["content", "assets", "dist"]

    # Another book still gets default
    assert manager.get_explorer_expanded_sections("book-2") == ["content", "resources"]


