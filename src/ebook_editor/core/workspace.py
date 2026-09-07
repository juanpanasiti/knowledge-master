"""Ebook workspace and chapter content manager."""

import base64
import re
from dataclasses import dataclass
from pathlib import Path
from natsort import natsorted

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.models import EbookMetadata

# Minimal 1x1 dark slate PNG bytes to serve as a valid default cover image
_DEFAULT_COVER_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
    "eM9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


def get_default_cover_bytes() -> bytes:
    """Return valid binary PNG data for the default cover."""
    return base64.b64decode(_DEFAULT_COVER_PNG_BASE64)


def slugify(value: str) -> str:
    """Generate a clean filesystem-friendly slug from title."""
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value) or "untitled-ebook"


@dataclass
class WorkspaceFile:
    """Represents an editable text or markdown file inside content/ or resources/."""

    path: Path
    name: str
    category: str = "content"  # "content" or "resources"

    @property
    def title(self) -> str:
        """Display title with the extension stripped."""
        return self.path.stem

    def read_content(self) -> str:
        """Read text from this file."""
        return self.path.read_text(encoding="utf-8")

    def write_content(self, content: str) -> None:
        """Atomically persist content to this file."""
        temp_file = self.path.with_name(f".{self.path.name}.tmp")
        temp_file.write_text(content, encoding="utf-8")
        temp_file.replace(self.path)


# Backward-compatible alias for existing chapter references
ChapterFile = WorkspaceFile


class EbookWorkspace:
    """Encapsulates a single local ebook project workspace."""

    def __init__(self, root_path: Path) -> None:
        self.root = root_path.expanduser().resolve()
        self.metadata_path = self.root / "metadata.json"
        self.assets_dir = self.root / "assets"
        self.content_dir = self.root / "content"
        self.resources_dir = self.root / "resources"
        self.dist_dir = self.root / "dist"

    def is_valid(self) -> bool:
        """Check if this folder contains a readable metadata.json file."""
        return self.root.is_dir() and self.metadata_path.is_file()

    def ensure_structure(self) -> None:
        """Ensure that assets, content, resources, and dist subdirectories exist."""
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        cover_path = self.assets_dir / "cover.png"
        if not cover_path.exists():
            cover_path.write_bytes(get_default_cover_bytes())

    def ensure_dist_dir(self) -> Path:
        """Ensure that the dist/ directory exists and return its path."""
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        return self.dist_dir

    def load_metadata(self) -> EbookMetadata:
        """Read and validate metadata.json."""
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Missing metadata.json in {self.root}")
        return EbookMetadata.load_from_file(self.metadata_path)

    def save_metadata(self, metadata: EbookMetadata) -> None:
        """Persist metadata to metadata.json."""
        metadata.save_to_file(self.metadata_path)

    def list_content_files(self) -> list[WorkspaceFile]:
        """List all markdown files in content/ sorted with natural hierarchical sorting."""
        if not self.content_dir.exists():
            return []
        md_files = [
            f for f in self.content_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".md"
        ]
        sorted_paths = natsorted(md_files, key=lambda p: p.name)
        return [WorkspaceFile(path=p, name=p.name, category="content") for p in sorted_paths]

    def list_chapters(self) -> list[ChapterFile]:
        """Backward-compatible alias for list_content_files()."""
        return self.list_content_files()

    def list_resource_files(self) -> list[WorkspaceFile]:
        """List all supplementary files in resources/ sorted naturally."""
        if not self.resources_dir.exists():
            return []
        files = [
            f for f in self.resources_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        sorted_paths = natsorted(files, key=lambda p: p.name)
        return [WorkspaceFile(path=p, name=p.name, category="resources") for p in sorted_paths]

    def list_asset_files(self) -> list[Path]:
        """List all media files in assets/ sorted naturally."""
        if not self.assets_dir.exists():
            return []
        files = [
            f for f in self.assets_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        return natsorted(files, key=lambda p: p.name)

    def list_dist_files(self) -> list[Path]:
        """List all generated deliverable files in dist/ sorted naturally."""
        if not self.dist_dir.exists():
            return []
        files = [
            f for f in self.dist_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        return natsorted(files, key=lambda p: p.name)

    def create_chapter(self, title_or_filename: str, content: str = "") -> ChapterFile:
        """Create a new chapter markdown file in content/."""
        self.ensure_structure()
        filename = title_or_filename.strip()
        if not filename.lower().endswith(".md"):
            filename = f"{filename}.md"
        target_path = self.content_dir / filename
        if target_path.exists():
            raise FileExistsError(f"Chapter '{filename}' already exists.")
        target_path.write_text(content, encoding="utf-8")
        return WorkspaceFile(path=target_path, name=target_path.name, category="content")

    def rename_chapter(self, old_name: str, new_title_or_name: str) -> ChapterFile:
        """Rename an existing chapter file."""
        clean_old = old_name if old_name.lower().endswith(".md") else f"{old_name}.md"
        source_path = self.content_dir / clean_old
        if not source_path.exists():
            raise FileNotFoundError(f"Chapter '{old_name}' not found.")

        clean_new = new_title_or_name.strip()
        if not clean_new.lower().endswith(".md"):
            clean_new = f"{clean_new}.md"
        dest_path = self.content_dir / clean_new
        if dest_path.exists() and dest_path != source_path:
            raise FileExistsError(f"Chapter '{clean_new}' already exists.")

        source_path.rename(dest_path)
        return WorkspaceFile(path=dest_path, name=dest_path.name, category="content")

    def delete_chapter(self, name: str) -> None:
        """Delete a chapter file from content/."""
        clean_name = name if name.lower().endswith(".md") else f"{name}.md"
        target_path = self.content_dir / clean_name
        if target_path.exists():
            target_path.unlink()

    def create_resource(self, filename: str, content: str = "") -> WorkspaceFile:
        """Create a new resource file in resources/."""
        self.ensure_structure()
        clean_name = filename.strip()
        if not clean_name:
            raise ValueError("Filename cannot be empty.")
        target_path = self.resources_dir / clean_name
        if target_path.exists():
            raise FileExistsError(f"Resource '{clean_name}' already exists.")
        target_path.write_text(content, encoding="utf-8")
        return WorkspaceFile(path=target_path, name=target_path.name, category="resources")

    def rename_resource(self, old_name: str, new_name: str) -> WorkspaceFile:
        """Rename an existing resource file."""
        clean_old = old_name.strip()
        source_path = self.resources_dir / clean_old
        if not source_path.exists():
            raise FileNotFoundError(f"Resource '{clean_old}' not found.")

        clean_new = new_name.strip()
        if not clean_new:
            raise ValueError("New filename cannot be empty.")
        dest_path = self.resources_dir / clean_new
        if dest_path.exists() and dest_path != source_path:
            raise FileExistsError(f"Resource '{clean_new}' already exists.")

        source_path.rename(dest_path)
        return WorkspaceFile(path=dest_path, name=dest_path.name, category="resources")

    def delete_resource(self, name: str) -> None:
        """Delete a resource file from resources/."""
        target_path = self.resources_dir / name.strip()
        if target_path.exists():
            target_path.unlink()

    def save_asset(self, filename: str, data: bytes) -> Path:
        """Save a media file into the ebook's assets directory."""
        self.ensure_structure()
        safe_filename = Path(filename).name
        target = self.assets_dir / safe_filename
        target.write_bytes(data)
        return target

    def delete_asset(self, filename: str) -> None:
        """Delete an asset file from assets/."""
        target = self.assets_dir / Path(filename).name
        if target.exists():
            target.unlink()

    def delete_dist(self, filename: str) -> None:
        """Delete a generated build file from dist/."""
        target = self.dist_dir / Path(filename).name
        if target.exists():
            target.unlink()


class WorkspaceManager:
    """Orchestrates ebook projects, discovery, and creation."""

    def __init__(self, config_manager: ConfigManager | None = None) -> None:
        self.config_manager = config_manager or ConfigManager()
        self.config_manager.ensure_directories()

    def discover_ebooks(self) -> list[EbookWorkspace]:
        """Scan ebooks directory and return all valid ebook workspaces."""
        discovered: list[EbookWorkspace] = []
        ebooks_dir = self.config_manager.ebooks_dir
        if not ebooks_dir.exists():
            return discovered

        for item in ebooks_dir.iterdir():
            if item.is_dir():
                workspace = EbookWorkspace(item)
                if workspace.is_valid():
                    discovered.append(workspace)

        return natsorted(discovered, key=lambda ws: ws.root.name)

    def create_ebook(
        self,
        title: str,
        author: str,
        description: str = "",
        folder_name: str | None = None,
        parent_dir: Path | None = None,
    ) -> EbookWorkspace:
        """Create a new standardized ebook project on disk."""
        target_parent = (parent_dir or self.config_manager.ebooks_dir).expanduser().resolve()
        target_parent.mkdir(parents=True, exist_ok=True)

        folder_slug = folder_name or slugify(title)
        book_dir = target_parent / folder_slug

        # Ensure directory is unique
        counter = 1
        base_dir = book_dir
        while book_dir.exists():
            book_dir = target_parent / f"{base_dir.name}-{counter}"
            counter += 1

        book_dir.mkdir(parents=True)
        workspace = EbookWorkspace(book_dir)
        workspace.ensure_structure()

        # Initialize metadata.json
        metadata = EbookMetadata(
            title=title,
            author=author,
            description=description,
            cover_path="assets/cover.png",
        )
        workspace.save_metadata(metadata)

        # Create initial chapter
        workspace.create_chapter(
            "1",
            f"# {title}\n\nStart writing your ebook here...\n",
        )

        # Track in recent ebooks
        self.config_manager.add_recent_ebook(book_dir)

        return workspace

    def open_ebook(self, path: Path | str) -> EbookWorkspace:
        """Open an existing ebook workspace and record in recent list."""
        book_dir = Path(path).expanduser().resolve()
        workspace = EbookWorkspace(book_dir)
        if not workspace.is_valid():
            raise ValueError(f"Directory {book_dir} is not a valid ebook (missing metadata.json)")

        workspace.ensure_structure()
        self.config_manager.add_recent_ebook(book_dir)
        return workspace
