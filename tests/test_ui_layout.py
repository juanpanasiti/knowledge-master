"""Tests for layout CSS hierarchy, editor scrolling, and width mode switching."""

from pathlib import Path
import pytest

from ebook_editor.main import GLOBAL_STYLES
from ebook_editor.ui.components.editor import VDITOR_HEAD_HTML, VditorEditor


def test_global_styles_full_height_chain():
    """Verify that GLOBAL_STYLES establishes a full-height flex column chain across Quasar containers."""
    assert "#app" in GLOBAL_STYLES
    assert ".q-layout" in GLOBAL_STYLES
    assert ".q-page-container" in GLOBAL_STYLES
    assert ".q-page" in GLOBAL_STYLES
    assert ".nicegui-content" in GLOBAL_STYLES
    assert "height: 100% !important;" in GLOBAL_STYLES
    assert "max-height: 100% !important;" in GLOBAL_STYLES
    assert "min-height: 0 !important;" in GLOBAL_STYLES
    assert "overflow: hidden !important;" in GLOBAL_STYLES
    assert "flex-direction: column !important;" in GLOBAL_STYLES


def test_vditor_styles_sheet_scrolling_and_width_modes():
    """Verify that VDITOR_HEAD_HTML defines sheet scrolling and width mode classes."""
    assert ".vditor-ir" in VDITOR_HEAD_HTML
    assert "overflow-y: auto !important;" in VDITOR_HEAD_HTML
    assert ".editor-sheet-centered" in VDITOR_HEAD_HTML
    assert ".editor-sheet-full" in VDITOR_HEAD_HTML
    assert "max-width: 56rem !important;" in VDITOR_HEAD_HTML
    assert "max-width: 100% !important;" in VDITOR_HEAD_HTML
    assert ".vditor-reset ol" in VDITOR_HEAD_HTML
    assert "list-style-type: decimal !important;" in VDITOR_HEAD_HTML
    assert ".vditor-reset table" in VDITOR_HEAD_HTML
    assert ".vditor-reset table th" in VDITOR_HEAD_HTML
    assert ".vditor-toolbar .vditor-tooltipped::after" in VDITOR_HEAD_HTML
    assert "'outdent'" in VDITOR_HEAD_HTML
    assert "'indent'" in VDITOR_HEAD_HTML
    assert "handleListEscape" in VDITOR_HEAD_HTML


def test_vditor_editor_width_mode_toggle():
    """Verify that VditorEditor initializes with width mode and toggles classes cleanly."""
    editor = VditorEditor(initial_value="Test content", width_mode="centered")
    assert "editor-sheet-centered" in editor.wrapper.classes
    assert "editor-sheet-full" not in editor.wrapper.classes

    editor.set_width_mode("full")
    assert "editor-sheet-full" in editor.wrapper.classes
    assert "editor-sheet-centered" not in editor.wrapper.classes

    editor.set_width_mode("centered")
    assert "editor-sheet-centered" in editor.wrapper.classes
    assert "editor-sheet-full" not in editor.wrapper.classes


def test_vditor_editor_autosave_unpacking():
    """Verify that _handle_autosave safely extracts content from detail or direct payload."""
    saved = []
    editor = VditorEditor(initial_value="", on_save=lambda c: saved.append(c))

    # 1. CustomEvent with detail.content (browser payload in NiceGUI)
    class MockEventDetail:
        args = {"detail": {"content": "Hello World"}, "type": "editor-autosave"}

    editor._handle_autosave(MockEventDetail())
    assert editor.content == "Hello World"
    assert saved == ["Hello World"]

    # 2. Direct content dictionary fallback
    class MockEventDirect:
        args = {"content": "Direct Content"}

    editor._handle_autosave(MockEventDirect())
    assert editor.content == "Direct Content"
    assert saved[-1] == "Direct Content"


def test_vditor_head_html_javascript_syntax():
    """Verify that all client-side JavaScript in VDITOR_HEAD_HTML is syntactically valid."""
    import subprocess
    import shutil

    if not shutil.which("node"):
        return  # Skip if node is not in environment

    start = VDITOR_HEAD_HTML.find("<script>") + len("<script>")
    end = VDITOR_HEAD_HTML.rfind("</script>")
    js_code = VDITOR_HEAD_HTML[start:end]

    res = subprocess.run(["node", "-c"], input=js_code, text=True, capture_output=True)
    assert res.returncode == 0, f"JavaScript syntax error in VDITOR_HEAD_HTML:\n{res.stderr}"


@pytest.mark.asyncio
async def test_cover_upload_and_manual_image_insert(tmp_path: Path):
    """Verify that cover upload and image insert correctly handle NiceGUI 3 FileUpload objects."""
    from nicegui.elements.upload_files import SmallFileUpload
    from ebook_editor.core.models import EbookMetadata
    from ebook_editor.core.workspace import EbookWorkspace
    from ebook_editor.ui.state import AppState
    from ebook_editor.ui.components.metadata_panel import MetadataPanelComponent
    from ebook_editor.ui.workspace_view import WorkspaceView

    from ebook_editor.core.config import ConfigManager
    ws = EbookWorkspace(tmp_path / "ebook")
    ws.ensure_structure()
    ws.save_metadata(EbookMetadata(title="Test Ebook", author="Test Author"))
    state = AppState(config_manager=ConfigManager(root_dir=tmp_path))
    state.current_workspace = ws

    class MockDialog:
        value = True
        closed = False
        def close(self):
            self.closed = True
            self.value = False

    # 1. Test cover upload
    panel = MetadataPanelComponent(state)
    file_cover = SmallFileUpload(name="new_cover.png", content_type="image/png", _data=b"COVER_BYTES")
    cover_event = type("MockEvent", (), {"file": file_cover})()
    dialog = MockDialog()

    await panel._handle_cover_upload(cover_event, dialog)
    assert dialog.closed is True
    assert (ws.assets_dir / "cover.png").read_bytes() == b"COVER_BYTES"
    meta = ws.load_metadata()
    assert meta.cover_path == "assets/cover.png"

    # 2. Test manual image insert into workspace
    class MockEditor:
        content = "# Chapter\n"
        def set_content(self, c):
            self.content = c

    class MockWorkspaceView:
        def __init__(self, s, ed):
            self.state = s
            self.editor = ed
        _handle_manual_image_insert = WorkspaceView._handle_manual_image_insert
        def _handle_editor_save(self, c):
            pass

    mock_ed = MockEditor()
    ws_view = MockWorkspaceView(state, mock_ed)
    chapter = ws.create_chapter("1 - Chapter 1", "# Chapter 1\n")
    state.active_chapter = chapter

    file_img = SmallFileUpload(name="diagram.png", content_type="image/png", _data=b"DIAGRAM_BYTES")
    img_event = type("MockEvent", (), {"file": file_img})()
    img_dialog = MockDialog()

    await ws_view._handle_manual_image_insert(img_event, img_dialog)
    assert img_dialog.closed is True
    assert (ws.assets_dir / "diagram.png").read_bytes() == b"DIAGRAM_BYTES"
    assert "./assets/diagram.png" in mock_ed.content


def test_workspace_view_switching_content_and_resources(tmp_path: Path):
    """Verify that selecting a content or resource file updates the editor content and title."""
    from ebook_editor.core.workspace import EbookWorkspace
    from ebook_editor.ui.state import AppState
    from ebook_editor.ui.workspace_view import WorkspaceView

    ws = EbookWorkspace(tmp_path / "book")
    ws.ensure_structure()
    ch1 = ws.create_chapter("01 - Intro", "# Introduction")
    res1 = ws.create_resource("architecture.mmd", "graph TD; A-->B;")

    from ebook_editor.core.config import ConfigManager
    state = AppState(config_manager=ConfigManager(root_dir=tmp_path))
    state.set_active_workspace(ws)

    class MockLabel:
        def __init__(self):
            self.text = ""
        def set_text(self, t):
            self.text = t
        def classes(self, **kwargs):
            pass

    class MockEditor:
        def __init__(self):
            self.content = ""
        def set_content(self, c):
            self.content = c

    wv = WorkspaceView.__new__(WorkspaceView)
    wv.state = state
    wv.editor = MockEditor()
    wv._chapter_title_label = MockLabel()
    wv._word_count_label = MockLabel()
    wv._save_status_label = MockLabel()
    wv._right_panel_tab = "metadata"
    wv.git_panel = None

    # Switch to chapter
    wv._handle_chapter_selected(ch1)
    assert wv._chapter_title_label.text == "01 - Intro"
    assert wv.editor.content == "# Introduction"

    # Switch to resource
    wv._handle_chapter_selected(res1)
    assert wv._chapter_title_label.text == "architecture.mmd"
    assert wv.editor.content == "graph TD; A-->B;"

    # Test save on active resource
    wv.state.set_active_file(res1)
    wv._handle_editor_save("graph TD; A-->B; B-->C;")
    assert res1.read_content() == "graph TD; A-->B; B-->C;"

