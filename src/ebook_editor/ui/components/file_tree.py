"""Sidebar file explorer component for chapters in content/."""

from typing import Callable
from nicegui import ui

from ebook_editor.core.workspace import ChapterFile, EbookWorkspace
from ebook_editor.ui.state import AppState


class FileTreeComponent:
    """Displays chapters with natural sorting, hidden extensions, and CRUD actions."""

    def __init__(
        self,
        state: AppState,
        on_select_chapter: Callable[[ChapterFile], None],
    ) -> None:
        self.state = state
        self.on_select_chapter = on_select_chapter
        self.container: ui.column | None = None

    def render(self) -> None:
        """Render the chapter explorer sidebar."""
        if self.container is None:
            self.container = ui.column().classes("w-full h-full flex-1 min-h-0 flex flex-col p-3 gap-2 select-none items-stretch overflow-hidden")
        else:
            self.container.clear()
        ws = self.state.current_workspace
        if not ws:
            return

        chapters = ws.list_chapters()

        with self.container:
            # Header
            with ui.row().classes("w-full flex-shrink-0 items-center justify-between px-2 py-1.5 border-b border-gray-700/50"):
                with ui.row().classes("items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-400"):
                    ui.icon("folder", size="1rem").classes("text-indigo-400")
                    ui.label("Chapters")

                ui.button(
                    icon="add",
                    on_click=self._show_new_chapter_dialog,
                ).props("round dense size=xs").classes("bg-indigo-600 hover:bg-indigo-700 text-white shadow").tooltip("New Chapter")

            # Scrollable chapter list
            with ui.column().classes("w-full flex-1 min-h-0 overflow-y-auto gap-1 p-1 items-stretch"):
                if not chapters:
                    with ui.column().classes("w-full p-4 items-center text-center"):
                        ui.label("No chapters yet.").classes("text-xs text-gray-500")
                        ui.button("Create First Chapter", on_click=self._show_new_chapter_dialog).props("outline size=sm").classes("mt-2")
                    return

                for chapter in chapters:
                    self._render_chapter_item(chapter)

    def _render_chapter_item(self, chapter: ChapterFile) -> None:
        is_active = (
            self.state.active_chapter is not None
            and self.state.active_chapter.name == chapter.name
        )

        item_classes = (
            "w-full px-2.5 py-1.5 rounded flex flex-row items-center justify-between text-xs cursor-pointer transition-colors group "
        )
        if is_active:
            item_classes += "bg-indigo-600/30 text-indigo-300 font-medium border-l-2 border-indigo-500"
        else:
            item_classes += "text-gray-300 hover:bg-gray-800/80 hover:text-gray-100"

        with ui.element("div").classes(item_classes):
            # Title with file icon
            with ui.row().classes("items-center gap-2 flex-grow truncate").on(
                "click", lambda _, ch=chapter: self._handle_select(ch)
            ):
                ui.icon("description", size="0.9rem").classes("text-gray-400 group-hover:text-indigo-300")
                ui.label(chapter.title).classes("truncate")

            # Action menu (rename / delete)
            with ui.button(icon="more_vert").props("flat round dense size=xs").classes(
                "opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition-opacity"
            ):
                with ui.menu().classes("bg-gray-800 text-white border border-gray-700"):
                    ui.menu_item("Rename", on_click=lambda _, ch=chapter: self._show_rename_dialog(ch))
                    ui.menu_item("Delete", on_click=lambda _, ch=chapter: self._show_delete_dialog(ch)).classes("text-red-400 hover:bg-red-950/40")

    def _handle_select(self, chapter: ChapterFile) -> None:
        self.state.set_active_chapter(chapter)
        self.render()
        self.on_select_chapter(chapter)

    def _show_new_chapter_dialog(self) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3"):
            ui.label("New Chapter").classes("text-base font-semibold")
            name_input = ui.input("Filename or Title", placeholder="e.g. 1.2 - Introduction").classes("w-full")

            def handle_create() -> None:
                val = name_input.value.strip()
                if not val:
                    ui.notify("Name cannot be empty", type="warning")
                    return
                dialog.close()
                ws = self.state.current_workspace
                if ws:
                    try:
                        new_ch = ws.create_chapter(val, f"# {val}\n\n")
                        self.state.set_active_chapter(new_ch)
                        self.render()
                        self.on_select_chapter(new_ch)
                        ui.notify(f"Created '{new_ch.title}'", type="positive")
                    except Exception as e:
                        ui.notify(str(e), type="negative")

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Create", on_click=handle_create).classes("bg-indigo-600 text-white size=sm")

        dialog.open()

    def _show_rename_dialog(self, chapter: ChapterFile) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3"):
            ui.label(f"Rename Chapter").classes("text-base font-semibold")
            name_input = ui.input("New Title", value=chapter.title).classes("w-full")

            def handle_rename() -> None:
                val = name_input.value.strip()
                if not val or val == chapter.title:
                    dialog.close()
                    return
                dialog.close()
                ws = self.state.current_workspace
                if ws:
                    try:
                        renamed = ws.rename_chapter(chapter.name, val)
                        if self.state.active_chapter and self.state.active_chapter.name == chapter.name:
                            self.state.set_active_chapter(renamed)
                        self.render()
                        ui.notify(f"Renamed to '{renamed.title}'", type="positive")
                    except Exception as e:
                        ui.notify(str(e), type="negative")

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Rename", on_click=handle_rename).classes("bg-indigo-600 text-white size=sm")

        dialog.open()

    def _show_delete_dialog(self, chapter: ChapterFile) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3"):
            ui.label("Delete Chapter?").classes("text-base font-semibold text-red-400")
            ui.label(f"Are you sure you want to delete '{chapter.title}.md'? This cannot be undone.").classes("text-xs text-gray-300")

            def handle_delete() -> None:
                dialog.close()
                ws = self.state.current_workspace
                if ws:
                    ws.delete_chapter(chapter.name)
                    if self.state.active_chapter and self.state.active_chapter.name == chapter.name:
                        remaining = ws.list_chapters()
                        next_ch = remaining[0] if remaining else None
                        self.state.set_active_chapter(next_ch)
                        if next_ch:
                            self.on_select_chapter(next_ch)
                    self.render()
                    ui.notify(f"Deleted '{chapter.title}'", type="info")

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Delete", on_click=handle_delete).classes("bg-red-600 text-white size=sm")

        dialog.open()
