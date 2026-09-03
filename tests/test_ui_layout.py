"""Tests for layout CSS hierarchy, editor scrolling, and width mode switching."""

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
