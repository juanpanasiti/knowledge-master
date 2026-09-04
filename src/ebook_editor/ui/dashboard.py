"""Dashboard view for browsing, opening, and creating ebook projects."""

from pathlib import Path
from typing import Callable
from nicegui import ui

from ebook_editor.core.models import EbookMetadata
from ebook_editor.core.workspace import EbookWorkspace
from ebook_editor.ui.state import AppState


class DashboardView:
    """Dashboard page showing recent projects, discovery, and creation dialogs."""

    def __init__(
        self,
        state: AppState,
        on_open_workspace: Callable[[EbookWorkspace], None],
    ) -> None:
        self.state = state
        self.on_open_workspace = on_open_workspace
        self.container: ui.column | None = None

    def render(self) -> None:
        """Render the complete dashboard view."""
        if self.container is None:
            self.container = ui.column().classes("w-full h-full flex-1 min-h-0 p-8 max-w-6xl mx-auto flex flex-col items-stretch overflow-hidden")
        else:
            self.container.clear()
        with self.container:
            # Header
            with ui.row().classes("w-full flex-shrink-0 items-center justify-between pb-6 border-b border-gray-700"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("menu_book", size="2.5rem").classes("text-indigo-400")
                    with ui.column().classes("gap-0"):
                        ui.label("Knowledge Master").classes("text-2xl font-bold")
                        ui.label("Local Markdown Ebook Studio").classes("text-sm text-gray-400")

                with ui.row().classes("items-center gap-3"):
                    ui.button("Open Folder", icon="folder_open", on_click=self._show_open_dialog).props("outline")
                    ui.button("New Ebook", icon="add", on_click=self._show_create_dialog).classes("bg-indigo-600 hover:bg-indigo-700 text-white")

            # Content grid
            with ui.row().classes("w-full flex-1 min-h-0 mt-6 gap-8 items-stretch overflow-hidden"):
                # Left Column: Recent Ebooks
                with ui.column().classes("flex-1 min-w-0 h-full flex flex-col gap-4 overflow-hidden"):
                    ui.label("Recent Projects").classes("text-lg font-semibold text-gray-200 flex-shrink-0")
                    self._render_recent_list()

                # Right Column: Discovered Ebooks in workspace root
                with ui.column().classes("flex-1 min-w-0 h-full flex flex-col gap-4 overflow-hidden"):
                    ui.label("Workspace Library").classes("text-lg font-semibold text-gray-200 flex-shrink-0")
                    self._render_discovered_list()

    def _render_recent_list(self) -> None:
        settings = self.state.config_manager.load_settings()
        recent_paths = settings.recent_ebooks

        if not recent_paths:
            with ui.card().classes("w-full p-6 text-center border border-dashed border-gray-700 bg-transparent"):
                ui.label("No recent ebooks opened yet.").classes("text-gray-400 text-sm")
            return

        with ui.column().classes("w-full flex-1 min-h-0 overflow-y-auto pr-2 pb-6 gap-2"):
            for path_str in recent_paths:
                p = Path(path_str)
                if not p.exists():
                    continue

                ws = EbookWorkspace(p)
                title = p.name
                author = ""
                if ws.is_valid():
                    try:
                        meta = ws.load_metadata()
                        title = meta.title
                        author = meta.author
                    except Exception:
                        pass

                with ui.card().classes(
                    "w-full p-3 flex flex-row items-center justify-between cursor-pointer hover:bg-gray-800 transition rounded border border-gray-700"
                ):
                    with ui.row().classes("items-center gap-3 flex-grow").on("click", lambda _, w=ws: self.on_open_workspace(w)):
                        ui.icon("book", size="1.8rem").classes("text-indigo-400")
                        with ui.column().classes("gap-0"):
                            ui.label(title).classes("font-semibold text-sm")
                            if author:
                                ui.label(f"by {author}").classes("text-xs text-gray-400")
                            ui.label(str(p)).classes("text-xs text-gray-500 truncate max-w-xs")

                    ui.button(
                        icon="close",
                        on_click=lambda _, ps=path_str: self._remove_recent(ps),
                    ).props("flat round dense size=sm").classes("text-gray-400 hover:text-red-400").tooltip("Remove from recent")

    def _render_discovered_list(self) -> None:
        discovered = self.state.workspace_manager.discover_ebooks()
        if not discovered:
            with ui.card().classes("w-full p-6 text-center border border-dashed border-gray-700 bg-transparent"):
                ui.label(f"No ebooks found in {self.state.config_manager.ebooks_dir}").classes("text-gray-400 text-sm")
            return

        with ui.column().classes("w-full flex-1 min-h-0 overflow-y-auto pr-2 pb-6 gap-2"):
            for ws in discovered:
                title = ws.root.name
                author = ""
                try:
                    meta = ws.load_metadata()
                    title = meta.title
                    author = meta.author
                except Exception:
                    pass

                with ui.card().classes(
                    "w-full p-3 flex flex-row items-center justify-between cursor-pointer hover:bg-gray-800 transition rounded border border-gray-700"
                ).on("click", lambda _, w=ws: self.on_open_workspace(w)):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon("auto_stories", size="1.8rem").classes("text-teal-400")
                        with ui.column().classes("gap-0"):
                            ui.label(title).classes("font-semibold text-sm")
                            if author:
                                ui.label(f"by {author}").classes("text-xs text-gray-400")

                    ui.button("Open", icon="arrow_forward").props("flat dense size=sm").classes("text-indigo-400")

    def _remove_recent(self, path_str: str) -> None:
        self.state.config_manager.remove_recent_ebook(path_str)
        self.render()

    def _show_create_dialog(self) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-96 p-6 gap-4"):
            ui.label("Create New Ebook").classes("text-lg font-bold")

            title_input = ui.input("Title", placeholder="e.g. Mastering OpenSpec").classes("w-full")
            author_input = ui.input("Author", placeholder="e.g. Jane Developer").classes("w-full")
            desc_input = ui.textarea("Description (optional)", placeholder="Brief summary of the book...").classes("w-full")

            def handle_create() -> None:
                title = title_input.value.strip()
                author = author_input.value.strip()
                if not title or not author:
                    ui.notify("Title and Author are required", type="warning")
                    return
                dialog.close()
                new_ws = self.state.workspace_manager.create_ebook(
                    title=title,
                    author=author,
                    description=desc_input.value.strip(),
                )
                ui.notify(f"Created ebook '{title}'", type="positive")
                self.on_open_workspace(new_ws)

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Create", on_click=handle_create).classes("bg-indigo-600 text-white")

        dialog.open()

    def _show_open_dialog(self) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-96 p-6 gap-4"):
            ui.label("Open Existing Ebook").classes("text-lg font-bold")
            path_input = ui.input("Directory Path", placeholder="e.g. /home/user/my-book").classes("w-full")

            def handle_open() -> None:
                path_val = path_input.value.strip()
                p = Path(path_val).expanduser().resolve()
                if not p.is_dir():
                    ui.notify("Path does not exist or is not a directory", type="negative")
                    return
                ws = EbookWorkspace(p)
                if not ws.is_valid():
                    ui.notify("Directory is missing metadata.json", type="negative")
                    return
                dialog.close()
                self.state.config_manager.add_recent_ebook(p)
                self.on_open_workspace(ws)

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Open", on_click=handle_open).classes("bg-indigo-600 text-white")

        dialog.open()
