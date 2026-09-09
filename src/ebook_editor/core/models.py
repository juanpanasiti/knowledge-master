"""Domain models for ebook metadata and application settings."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator


class EbookMetadata(BaseModel):
    """Metadata specification for a single ebook project."""

    title: str
    author: str
    description: str = Field(default="")
    cover_path: str = "assets/cover.png"
    tags: list[str] = Field(default_factory=list)
    finished: bool = Field(default=False, description="Whether the ebook is finalized for publication")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: str | None) -> str:
        if v is None:
            return ""
        return str(v)

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
    cover_size: str = "medium"
    window_width: int = 1280
    window_height: int = 800
    kindle_email: str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    workspace_ui_state: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-workspace UI states such as expanded explorer sections",
    )

    def get_explorer_expanded_sections(self, workspace_key: str) -> list[str]:
        """Return expanded accordion sections for a workspace, defaulting to content and resources."""
        state = self.workspace_ui_state.get(workspace_key, {})
        return list(state.get("expanded_sections", ["content", "resources"]))

    def set_explorer_expanded_sections(self, workspace_key: str, sections: list[str]) -> None:
        """Store expanded accordion sections for a workspace."""
        if workspace_key not in self.workspace_ui_state:
            self.workspace_ui_state[workspace_key] = {}
        self.workspace_ui_state[workspace_key]["expanded_sections"] = list(sections)

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

    def prune_invalid_recents(self) -> bool:
        """Remove paths that do not exist or lack metadata.json. Return True if changes were made."""
        valid: list[str] = []
        for p_str in self.recent_ebooks:
            p = Path(p_str)
            if p.is_dir() and (p / "metadata.json").is_file():
                valid.append(p_str)
        if valid != self.recent_ebooks:
            self.recent_ebooks = valid
            if self.last_opened_ebook and self.last_opened_ebook not in valid:
                self.last_opened_ebook = valid[0] if valid else None
            return True
        return False

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
