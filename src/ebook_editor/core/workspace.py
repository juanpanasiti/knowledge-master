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
class ChapterFile:
    """Represents a markdown chapter inside the ebook content directory."""

    path: Path
    name: str

    @property
    def title(self) -> str:
        """Display title with the .md extension stripped."""
        return self.path.stem

    def read_content(self) -> str:
        """Read text from this markdown file."""
        return self.path.read_text(encoding="utf-8")

    def write_content(self, content: str) -> None:
        """Atomically persist content to this markdown file."""
        temp_file = self.path.with_suffix(".tmp")
        temp_file.write_text(content, encoding="utf-8")
        temp_file.replace(self.path)


class EbookWorkspace:
    """Encapsulates a single local ebook project workspace."""

    def __init__(self, root_path: Path) -> None:
        self.root = root_path.expanduser().resolve()
        self.metadata_path = self.root / "metadata.json"
        self.assets_dir = self.root / "assets"
        self.content_dir = self.root / "content"
        self.dist_dir = self.root / "dist"

    def is_valid(self) -> bool:
        """Check if this folder contains a readable metadata.json file."""
        return self.root.is_dir() and self.metadata_path.is_file()

    def ensure_structure(self) -> None:
        """Ensure that assets, content, and dist subdirectories exist."""
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)
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

    def list_chapters(self) -> list[ChapterFile]:
        """List all markdown files in content/ sorted with natural hierarchical sorting."""
        if not self.content_dir.exists():
            return []
        md_files = [
            f for f in self.content_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".md"
        ]
        sorted_paths = natsorted(md_files, key=lambda p: p.name)
        return [ChapterFile(path=p, name=p.name) for p in sorted_paths]

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
        return ChapterFile(path=target_path, name=target_path.name)

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
        return ChapterFile(path=dest_path, name=dest_path.name)

    def delete_chapter(self, name: str) -> None:
        """Delete a chapter file from content/."""
        clean_name = name if name.lower().endswith(".md") else f"{name}.md"
        target_path = self.content_dir / clean_name
        if target_path.exists():
            target_path.unlink()

    def save_asset(self, filename: str, data: bytes) -> Path:
        """Save a media file into the ebook's assets directory."""
        self.ensure_structure()
        safe_filename = Path(filename).name
        target = self.assets_dir / safe_filename
        target.write_bytes(data)
        return target


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
