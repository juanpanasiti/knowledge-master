"""Unit tests for AppState file switching and reactive notifications."""

from pathlib import Path
from ebook_editor.core.config import ConfigManager
from ebook_editor.core.workspace import EbookWorkspace, WorkspaceFile
from ebook_editor.ui.state import AppState


def test_app_state_file_switching(tmp_path: Path) -> None:
    config_mgr = ConfigManager(root_dir=tmp_path / "app")
    state = AppState(config_manager=config_mgr)

    ws = EbookWorkspace(tmp_path / "test-book")
    ws.ensure_structure()
    ws.create_chapter("intro", "# Intro")
    r1 = ws.create_resource("diagram.mmd", "graph TD; A-->B;")

    events: list[str] = []

    def on_changed(f: WorkspaceFile | None) -> None:
        if f:
            events.append(f.name)

    state.on_file_changed(on_changed)
    state.set_active_workspace(ws)

    # Initial active file is the first chapter
    assert state.active_file is not None
    assert state.active_file.name == "intro.md"
    assert state.active_chapter.name == "intro.md"

    # Switch to resource file
    state.set_active_file(r1)
    assert state.active_file.name == "diagram.mmd"
    assert state.active_file.category == "resources"
    assert state.active_chapter.name == "diagram.mmd"
    assert "diagram.mmd" in events
