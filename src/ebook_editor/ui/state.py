"""Shared state container for the Knowledge Master UI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.git_service import GitService
from ebook_editor.core.workspace import ChapterFile, EbookWorkspace, WorkspaceManager


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
        self.active_chapter: ChapterFile | None = None
        self.git_service: GitService | None = None

        settings = self.config_manager.load_settings()
        self.theme: str = settings.theme
        self.save_status: str = "Saved"
        self.word_count: int = 0

        # UI listeners for navigation and component state updates
        self._view_change_listeners: list[Callable[[str], None]] = []
        self._chapter_change_listeners: list[Callable[[ChapterFile | None], None]] = []
        self._workspace_change_listeners: list[Callable[[EbookWorkspace | None], None]] = []

    def set_active_workspace(self, workspace: EbookWorkspace | None) -> None:
        """Switch current active ebook workspace and initialize GitService."""
        self.current_workspace = workspace
        if workspace:
            self.git_service = GitService(workspace.root)
            chapters = workspace.list_chapters()
            self.active_chapter = chapters[0] if chapters else None
            self.config_manager.add_recent_ebook(workspace.root)
        else:
            self.git_service = None
            self.active_chapter = None

        for listener in self._workspace_change_listeners:
            listener(workspace)

    def set_active_chapter(self, chapter: ChapterFile | None) -> None:
        """Switch currently opened chapter in the editor."""
        self.active_chapter = chapter
        self.save_status = "Saved"
        for listener in self._chapter_change_listeners:
            listener(chapter)

    def on_workspace_changed(self, callback: Callable[[EbookWorkspace | None], None]) -> None:
        self._workspace_change_listeners.append(callback)

    def on_chapter_changed(self, callback: Callable[[ChapterFile | None], None]) -> None:
        self._chapter_change_listeners.append(callback)
