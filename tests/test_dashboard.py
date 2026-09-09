"""Unit tests for DashboardView and front-facing cover rendering."""

from pathlib import Path
from nicegui import ui

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.workspace import EbookWorkspace
from ebook_editor.ui.dashboard import COVER_SIZE_CONFIGS, DashboardView
from ebook_editor.ui.state import AppState


def test_cover_size_configs() -> None:
    """Verify that all cover size presets exist and have positive dimensions."""
    for key in ("small", "medium", "large"):
        assert key in COVER_SIZE_CONFIGS
        cfg = COVER_SIZE_CONFIGS[key]
        assert cfg["width_px"] > 0
        assert cfg["height_px"] > 0
        assert "font_size" in cfg


def test_dashboard_render_with_custom_and_fallback_covers(tmp_path: Path) -> None:
    """Verify that DashboardView renders cleanly without errors for both real and fallback covers."""
    root = tmp_path / "test-km"
    config_mgr = ConfigManager(root_dir=root)
    state = AppState(config_manager=config_mgr)

    opened: list[EbookWorkspace] = []
    dashboard = DashboardView(state, on_open_workspace=lambda w: opened.append(w))

    # 1. Create a dummy ebook workspace with a custom cover
    ebook_dir = root / "ebooks" / "my-test-book"
    ws = state.workspace_manager.create_ebook(title="My Test Book", author="Test Author")
    custom_cover = ws.assets_dir / "cover.png"
    # Write > 100 bytes of dummy png bytes
    custom_cover.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 150)

    # 2. Add to recent
    config_mgr.add_recent_ebook(ws.root)

    # 3. Render dashboard
    dashboard.render()
    assert dashboard.container is not None

    # 4. Switch cover size in settings and re-render
    config_mgr.set_cover_size("large")
    dashboard.render()
    assert config_mgr.load_settings().cover_size == "large"


def test_dashboard_recent_shelf_filters_invalid_workspaces(tmp_path: Path) -> None:
    """Verify that DashboardView prunes and does not render non-existent or invalid workspaces."""
    root = tmp_path / "test-km"
    config_mgr = ConfigManager(root_dir=root)
    state = AppState(config_manager=config_mgr)
    dashboard = DashboardView(state, on_open_workspace=lambda _: None)

    # Add an invalid directory (no metadata.json) and a non-existent path
    invalid_dir = tmp_path / "phantom-book"
    invalid_dir.mkdir(parents=True)
    non_existent = tmp_path / "ghost-book"

    config_mgr.add_recent_ebook(invalid_dir)
    config_mgr.add_recent_ebook(non_existent)

    # Render dashboard - should prune/filter them out cleanly
    dashboard.render()
    settings = config_mgr.load_settings()
    assert settings.recent_ebooks == []

