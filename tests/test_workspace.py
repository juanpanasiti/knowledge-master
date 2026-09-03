"""Unit tests for EbookWorkspace and WorkspaceManager."""

from pathlib import Path
import pytest

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.workspace import EbookWorkspace, WorkspaceManager


def test_create_ebook_structure(tmp_path: Path) -> None:
    config_mgr = ConfigManager(root_dir=tmp_path / "app")
    ws_mgr = WorkspaceManager(config_manager=config_mgr)

    ws = ws_mgr.create_ebook(
        title="Python Guide",
        author="Guido",
        description="A book about Python",
    )

    assert ws.is_valid()
    assert (ws.root / "metadata.json").is_file()
    assert (ws.root / "assets" / "cover.png").is_file()
    assert (ws.root / "content" / "1.md").is_file()

    meta = ws.load_metadata()
    assert meta.title == "Python Guide"
    assert meta.author == "Guido"

    chapters = ws.list_chapters()
    assert len(chapters) == 1
    assert chapters[0].name == "1.md"
    assert chapters[0].title == "1"
    assert "Python Guide" in chapters[0].read_content()


def test_natural_sorting_of_chapters(tmp_path: Path) -> None:
    ws = EbookWorkspace(tmp_path / "test-book")
    ws.ensure_structure()

    # Create files in mixed order
    filenames = [
        "1.10 - Advanced Topics.md",
        "00 - Course Introduction.md",
        "1 - Overview.md",
        "1.1 - Unit One.md",
        "1.2 - Unit Two.md",
        "1.1.1 - Detailed Concept.md",
        "2 - Next Chapter.md",
    ]
    for fn in filenames:
        (ws.content_dir / fn).write_text(f"# {fn}", encoding="utf-8")

    chapters = ws.list_chapters()
    ordered_titles = [c.title for c in chapters]

    expected = [
        "00 - Course Introduction",
        "1 - Overview",
        "1.1 - Unit One",
        "1.1.1 - Detailed Concept",
        "1.2 - Unit Two",
        "1.10 - Advanced Topics",
        "2 - Next Chapter",
    ]
    assert ordered_titles == expected


def test_chapter_crud_operations(tmp_path: Path) -> None:
    ws = EbookWorkspace(tmp_path / "test-book")
    ws.ensure_structure()

    # Create
    ch1 = ws.create_chapter("intro", "# Welcome")
    assert ch1.name == "intro.md"
    assert ch1.title == "intro"
    assert ch1.read_content() == "# Welcome"

    # Duplicate creation error
    with pytest.raises(FileExistsError):
        ws.create_chapter("intro", "# Conflict")

    # Rename
    ch_renamed = ws.rename_chapter("intro", "01 - Welcome")
    assert ch_renamed.name == "01 - Welcome.md"
    assert not (ws.content_dir / "intro.md").exists()
    assert (ws.content_dir / "01 - Welcome.md").exists()

    # Save content
    ch_renamed.write_content("# Welcome Updated")
    assert ch_renamed.read_content() == "# Welcome Updated"

    # Delete
    ws.delete_chapter("01 - Welcome")
    assert not (ws.content_dir / "01 - Welcome.md").exists()
    assert len(ws.list_chapters()) == 0


def test_workspace_discovery(tmp_path: Path) -> None:
    config_mgr = ConfigManager(root_dir=tmp_path / "app")
    ws_mgr = WorkspaceManager(config_manager=config_mgr)

    ws1 = ws_mgr.create_ebook("Book A", "Author A")
    ws2 = ws_mgr.create_ebook("Book B", "Author B")

    discovered = ws_mgr.discover_ebooks()
    assert len(discovered) == 2
    roots = [w.root for w in discovered]
    assert ws1.root in roots
    assert ws2.root in roots
