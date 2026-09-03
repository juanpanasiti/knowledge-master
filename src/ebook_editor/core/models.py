"""Domain models for ebook metadata and application settings."""

from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field


class EbookMetadata(BaseModel):
    """Metadata specification for a single ebook project."""

    title: str
    author: str
    description: str = ""
    cover_path: str = "assets/cover.png"
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def save_to_file(self, target_path: Path) -> None:
        """Serialize and write metadata to a JSON file."""
        self.updated_at = datetime.now(timezone.utc)
        target_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, file_path: Path) -> "EbookMetadata":
        """Load and parse metadata from a JSON file."""
        content = file_path.read_text(encoding="utf-8")
        return cls.model_validate_json(content)


class AppSettings(BaseModel):
    """Global configuration settings for the user workspace."""

    recent_ebooks: list[str] = Field(default_factory=list)
    last_opened_ebook: str | None = None
    theme: str = "dark"
    window_width: int = 1280
    window_height: int = 800

    def add_recent_ebook(self, path: str) -> None:
        """Add an ebook path to recent list, deduplicating and keeping the newest first."""
        normalized = str(Path(path).expanduser().resolve())
        if normalized in self.recent_ebooks:
            self.recent_ebooks.remove(normalized)
        self.recent_ebooks.insert(0, normalized)
        # Keep up to 20 recent ebooks
        self.recent_ebooks = self.recent_ebooks[:20]
        self.last_opened_ebook = normalized

    def remove_recent_ebook(self, path: str) -> None:
        """Remove an ebook path from the recent list."""
        normalized = str(Path(path).expanduser().resolve())
        if normalized in self.recent_ebooks:
            self.recent_ebooks.remove(normalized)
        if self.last_opened_ebook == normalized:
            self.last_opened_ebook = self.recent_ebooks[0] if self.recent_ebooks else None

    def save_to_file(self, target_path: Path) -> None:
        """Serialize and write settings to a JSON file."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, file_path: Path) -> "AppSettings":
        """Load and parse settings from a JSON file, or return defaults if missing."""
        if not file_path.exists():
            return cls()
        content = file_path.read_text(encoding="utf-8")
        return cls.model_validate_json(content)
