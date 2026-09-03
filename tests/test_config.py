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
