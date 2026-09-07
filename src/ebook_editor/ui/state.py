"""Shared state container for the Knowledge Master UI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.git_service import GitService
from ebook_editor.core.workspace import ChapterFile, EbookWorkspace, WorkspaceFile, WorkspaceManager


class AppState:
    """Central reactive state for the active UI session."""

    def __init__(
        self,
        config_manager: ConfigManager | None = None,
        workspace_manager: WorkspaceManager | None = None,
    ) -> None:
        self.config_manager = config_manager or ConfigManager()
        self.workspace_manager = workspace_manager or WorkspaceManager(self.config_manager)
        self.current_workspace: EbookWorkspace | None = None
        self.active_file: WorkspaceFile | None = None
        self.git_service: GitService | None = None

        settings = self.config_manager.load_settings()
        self.theme: str = settings.theme
        self.save_status: str = "Saved"
        self.word_count: int = 0

        # UI listeners for navigation and component state updates
        self._view_change_listeners: list[Callable[[str], None]] = []
        self._file_change_listeners: list[Callable[[WorkspaceFile | None], None]] = []
        self._workspace_change_listeners: list[Callable[[EbookWorkspace | None], None]] = []

    @property
    def active_chapter(self) -> ChapterFile | None:
        """Backward-compatible property alias for active_file."""
        return self.active_file

    @active_chapter.setter
    def active_chapter(self, value: ChapterFile | None) -> None:
        self.active_file = value

    def set_active_workspace(self, workspace: EbookWorkspace | None) -> None:
        """Switch current active ebook workspace and initialize GitService."""
        self.current_workspace = workspace
        if workspace:
            self.git_service = GitService(workspace.root)
            content_files = workspace.list_content_files()
            self.active_file = content_files[0] if content_files else None
            self.config_manager.add_recent_ebook(workspace.root)
        else:
            self.git_service = None
            self.active_file = None

        for listener in self._workspace_change_listeners:
            listener(workspace)

    def set_active_file(self, file: WorkspaceFile | None) -> None:
        """Switch currently opened file in the editor (content or resource)."""
        self.active_file = file
        self.save_status = "Saved"
        for listener in self._file_change_listeners:
            listener(file)

    def set_active_chapter(self, chapter: ChapterFile | None) -> None:
        """Backward-compatible alias for set_active_file."""
        self.set_active_file(chapter)

    def on_workspace_changed(self, callback: Callable[[EbookWorkspace | None], None]) -> None:
        self._workspace_change_listeners.append(callback)

    def on_file_changed(self, callback: Callable[[WorkspaceFile | None], None]) -> None:
        self._file_change_listeners.append(callback)

    def on_chapter_changed(self, callback: Callable[[ChapterFile | None], None]) -> None:
        """Backward-compatible alias for on_file_changed."""
        self.on_file_changed(callback)

