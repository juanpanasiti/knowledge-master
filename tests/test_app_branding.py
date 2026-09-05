"""Tests for application icon assets and branding."""

from pathlib import Path


def test_bundled_favicon_exists() -> None:
    """Verify that the packaged static favicon exists and is non-empty."""
    static_favicon = Path(__file__).parent.parent / "src" / "ebook_editor" / "static" / "favicon.png"
    assert static_favicon.is_file(), f"Favicon asset missing at {static_favicon}"
    assert static_favicon.stat().st_size > 10_000, "Favicon file appears truncated or empty"


def test_repository_icon_exists() -> None:
    """Verify that the master desktop icon exists and is non-empty."""
    repo_icon = Path(__file__).parent.parent / "assets" / "icon.png"
    assert repo_icon.is_file(), f"Repository icon missing at {repo_icon}"
    assert repo_icon.stat().st_size > 10_000, "Repository icon file appears truncated or empty"
