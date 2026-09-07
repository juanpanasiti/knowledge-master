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
    assert (ws.root / "resources").is_dir()
    assert (ws.root / "dist").is_dir()
    assert ws.ensure_dist_dir() == ws.root / "dist"

    meta = ws.load_metadata()
    assert meta.title == "Python Guide"
    assert meta.author == "Guido"

    chapters = ws.list_chapters()
    assert len(chapters) == 1
    assert chapters[0].name == "1.md"
    assert chapters[0].title == "1"
    assert "Python Guide" in chapters[0].read_content()


def test_resource_crud_and_multi_folder_listings(tmp_path: Path) -> None:
    ws = EbookWorkspace(tmp_path / "multi-test-book")
    ws.ensure_structure()

    assert ws.resources_dir.is_dir()
    assert len(ws.list_resource_files()) == 0

    # Create resources (e.g. .mmd diagram and .md notes)
    r1 = ws.create_resource("flowchart.mmd", "graph TD; A-->B;")
    assert r1.name == "flowchart.mmd"
    assert r1.category == "resources"
    assert r1.read_content() == "graph TD; A-->B;"

    r2 = ws.create_resource("notes.md", "# Research Notes")
    assert r2.name == "notes.md"
    assert r2.category == "resources"

    # Duplicate creation error
    with pytest.raises(FileExistsError):
        ws.create_resource("flowchart.mmd", "graph LR; X-->Y;")

    # Empty name error
    with pytest.raises(ValueError):
        ws.create_resource("   ")

    # List resources
    resources = ws.list_resource_files()
    assert len(resources) == 2
    assert [r.name for r in resources] == ["flowchart.mmd", "notes.md"]

    # Rename resource
    r1_renamed = ws.rename_resource("flowchart.mmd", "architecture.mmd")
    assert r1_renamed.name == "architecture.mmd"
    assert not (ws.resources_dir / "flowchart.mmd").exists()
    assert (ws.resources_dir / "architecture.mmd").exists()

    # Write content to resource
    r1_renamed.write_content("graph TD; Core-->UI;")
    assert r1_renamed.read_content() == "graph TD; Core-->UI;"

    # Assets & Dist listing
    ws.save_asset("sample.png", b"fake-png-data")
    assert len(ws.list_asset_files()) == 2  # cover.png and sample.png

    (ws.dist_dir / "book.pdf").write_bytes(b"%PDF-1.4")
    (ws.dist_dir / "book.epub").write_bytes(b"PK-fake-epub")
    dist_files = ws.list_dist_files()
    assert len(dist_files) == 2
    assert [f.name for f in dist_files] == ["book.epub", "book.pdf"]

    # Delete resource
    ws.delete_resource("architecture.mmd")
    assert len(ws.list_resource_files()) == 1

    # Delete asset and dist
    ws.delete_asset("sample.png")
    assert len(ws.list_asset_files()) == 1
    ws.delete_dist("book.pdf")
    assert len(ws.list_dist_files()) == 1


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
