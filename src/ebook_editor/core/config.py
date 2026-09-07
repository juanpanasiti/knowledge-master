"""Configuration manager for knowledge-master user workspace."""

from pathlib import Path
from ebook_editor.core.models import AppSettings

DEFAULT_APP_DIR = Path.home() / "knowledge-master"
CONFIG_FILE_NAME = "config.json"
EBOOKS_DIR_NAME = "ebooks"


class ConfigManager:
    """Manages root workspace directories and global user settings."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = (root_dir or DEFAULT_APP_DIR).expanduser().resolve()
        self.config_path = self.root_dir / CONFIG_FILE_NAME
        self.ebooks_dir = self.root_dir / EBOOKS_DIR_NAME

    def ensure_directories(self) -> None:
        """Create the central user root and default ebooks directory if not present."""
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.ebooks_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            default_settings = AppSettings()
            default_settings.save_to_file(self.config_path)

    def load_settings(self) -> AppSettings:
        """Load settings from config.json or initialize if missing."""
        self.ensure_directories()
        return AppSettings.load_from_file(self.config_path)

    def save_settings(self, settings: AppSettings) -> None:
        """Persist settings to config.json."""
        self.ensure_directories()
        settings.save_to_file(self.config_path)

    def add_recent_ebook(self, path: Path | str) -> AppSettings:
        """Add an ebook path to the recent list and save settings."""
        settings = self.load_settings()
        settings.add_recent_ebook(str(path))
        self.save_settings(settings)
        return settings

    def remove_recent_ebook(self, path: Path | str) -> AppSettings:
        """Remove an ebook path from the recent list and save settings."""
        settings = self.load_settings()
        settings.remove_recent_ebook(str(path))
        self.save_settings(settings)
        return settings

    def set_theme(self, theme: str) -> AppSettings:
        """Update active theme ('dark' or 'light') and persist."""
        settings = self.load_settings()
        settings.theme = theme
        self.save_settings(settings)
        return settings

    def set_cover_size(self, cover_size: str) -> AppSettings:
        """Update active cover card size preset ('small', 'medium', or 'large') and persist."""
        settings = self.load_settings()
        settings.cover_size = cover_size
        self.save_settings(settings)
        return settings

    def get_explorer_expanded_sections(self, workspace_key: str) -> list[str]:
        """Return expanded explorer sections for the specified workspace slug."""
        settings = self.load_settings()
        return settings.get_explorer_expanded_sections(workspace_key)

    def set_explorer_expanded_sections(self, workspace_key: str, sections: list[str]) -> AppSettings:
        """Update and persist expanded explorer sections for the specified workspace slug."""
        settings = self.load_settings()
        settings.set_explorer_expanded_sections(workspace_key, sections)
        self.save_settings(settings)
        return settings


