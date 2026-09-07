"""Unit tests for FileTreeComponent rendering and explorer behavior."""

from pathlib import Path
from ebook_editor.core.config import ConfigManager
from ebook_editor.core.workspace import EbookWorkspace, WorkspaceFile
from ebook_editor.ui.components.file_tree import FileTreeComponent, _format_size
from ebook_editor.ui.state import AppState


def test_format_size():
    assert _format_size(500) == "500 B"
    assert _format_size(1536) == "1.5 KB"
    assert _format_size(1024 * 1024 * 2) == "2.0 MB"


def test_file_tree_component_initialization(tmp_path: Path):
    config_mgr = ConfigManager(root_dir=tmp_path / "app")
    state = AppState(config_manager=config_mgr)

    ws = EbookWorkspace(tmp_path / "book")
    ws.ensure_structure()
    ws.create_chapter("intro", "# Intro")
    r1 = ws.create_resource("architecture.mmd", "graph TD; A-->B;")
    ws.save_asset("cover.png", b"fake")
    (ws.dist_dir / "book.pdf").write_bytes(b"%PDF")

    state.set_active_workspace(ws)

    selected: list[WorkspaceFile] = []
    tree = FileTreeComponent(state, on_select_chapter=lambda f: selected.append(f))

    # Check persistence integration
    slug = ws.root.name
    assert tree.state.config_manager.get_explorer_expanded_sections(slug) == ["content", "resources"]

    tree._handle_expansion_change("dist", True)
    assert "dist" in tree.state.config_manager.get_explorer_expanded_sections(slug)

    tree._handle_expansion_change("resources", False)
    assert "resources" not in tree.state.config_manager.get_explorer_expanded_sections(slug)

    # Test file selection
    tree._handle_select_file(r1)
    assert len(selected) == 1
    assert selected[0].name == "architecture.mmd"
    assert state.active_file.name == "architecture.mmd"
