"""Pytest test configuration and global fixtures."""

from pathlib import Path
import pytest
import ebook_editor.core.config as config_mod


@pytest.fixture(autouse=True)
def isolate_default_app_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests never write to user's real ~/knowledge-master directory."""
    test_app_dir = tmp_path / "test-knowledge-master"
    monkeypatch.setattr(config_mod, "DEFAULT_APP_DIR", test_app_dir)
