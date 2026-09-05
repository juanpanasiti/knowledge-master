"""Workspace view assembling file tree, Vditor editor, metadata, and git panels."""

from pathlib import Path
from typing import Callable
from nicegui import events, ui

from ebook_editor.core.workspace import ChapterFile, EbookWorkspace
from ebook_editor.ui.components.editor import VditorEditor
from ebook_editor.ui.components.export_dialog import ExportDialog
from ebook_editor.ui.components.file_tree import FileTreeComponent
from ebook_editor.ui.components.git_panel import GitPanelComponent
from ebook_editor.ui.components.metadata_panel import MetadataPanelComponent
from ebook_editor.ui.state import AppState


class WorkspaceView:
    """Active ebook editing view with split panes for explorer, editor, and inspector."""

    def __init__(
        self,
        state: AppState,
        on_back_to_dashboard: Callable[[], None],
    ) -> None:
        self.state = state
        self.on_back_to_dashboard = on_back_to_dashboard
        self.container: ui.column | None = None

        self.editor: VditorEditor | None = None
        self.file_tree: FileTreeComponent | None = None
        self.metadata_panel: MetadataPanelComponent | None = None
        self.git_panel: GitPanelComponent | None = None

        self._right_panel_tab = "metadata"  # "metadata" or "git"
        self._right_panel_visible = True
        self._editor_width_mode = "centered"  # "centered" or "full"
        self._save_status_label = None
        self._word_count_label = None
        self._width_toggle_btn = None
        self._right_panel_container = None

    def render(self) -> None:
        """Render the complete workspace layout."""
        if self.container is None:
            self.container = ui.column().classes("w-full h-full flex-1 min-h-0 p-0 gap-0 overflow-hidden items-stretch")
        else:
            self.container.clear()
        ws = self.state.current_workspace
        if not ws:
            return

        meta = ws.load_metadata()

        with self.container:
            # Top Application Header
            with ui.row().classes("w-full h-12 flex-shrink-0 px-4 items-center justify-between border-b border-gray-800 bg-gray-900 select-none z-10"):
                with ui.row().classes("items-center gap-3"):
                    ui.button(
                        icon="arrow_back",
                        on_click=self.on_back_to_dashboard,
                    ).props("flat round dense size=sm").classes("text-gray-400 hover:text-white").tooltip("Return to Library")

                    ui.icon("book", size="1.2rem").classes("text-indigo-400")
                    ui.label(meta.title).classes("font-semibold text-sm text-gray-200")
                    if meta.author:
                        ui.label(f"• {meta.author}").classes("text-xs text-gray-500")

                with ui.row().classes("items-center gap-2"):
                    # Export & Publish Button
                    ui.button(
                        "Export",
                        icon="ios_share",
                        on_click=self._show_export_dialog,
                    ).props("flat dense size=sm").classes("text-xs text-indigo-300 hover:text-white").tooltip("Export EPUB, PDF, and Send to Kindle")

                    # Clean Insert Image Button triggering dialog
                    ui.button(
                        "Insert Image",
                        icon="image",
                        on_click=self._show_insert_image_dialog,
                    ).props("flat dense size=sm").classes("text-xs text-gray-300").tooltip("Insert image from ebook assets")

                    # Right panel toggle tabs
                    ui.toggle(
                        options={"metadata": "Details", "git": "Git"},
                        value=self._right_panel_tab,
                        on_change=self._switch_right_tab,
                    ).props("dense rounded size=xs outline")

                    ui.button(
                        icon="view_sidebar",
                        on_click=self._toggle_right_panel,
                    ).props("flat round dense size=sm").classes("text-gray-400 hover:text-white").tooltip("Toggle Right Panel")

            # Main Body: 3-Column Split View
            with ui.row().classes("w-full flex-1 min-h-0 overflow-hidden gap-0 items-stretch"):
                # 1. Left Sidebar: Chapter File Tree (260px)
                with ui.column().classes("w-64 h-full border-r border-gray-800 bg-gray-900/50 flex-shrink-0 p-0 items-stretch overflow-hidden"):
                    self.file_tree = FileTreeComponent(
                        state=self.state,
                        on_select_chapter=self._handle_chapter_selected,
                    )
                    self.file_tree.render()

                # 2. Central Editor Column
                with ui.column().classes("flex-1 min-w-0 h-full p-0 gap-0 overflow-hidden bg-gray-950 items-stretch"):
                    # Editor Sub-header with chapter title and status
                    with ui.row().classes("w-full h-8 flex-shrink-0 px-4 items-center justify-between border-b border-gray-800/60 bg-gray-900/30 text-xs text-gray-400 select-none"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("edit_note", size="1rem").classes("text-indigo-400")
                            current_title = self.state.active_chapter.title if self.state.active_chapter else "No chapter selected"
                            self._chapter_title_label = ui.label(current_title).classes("font-medium text-gray-300")

                        with ui.row().classes("items-center gap-3 text-[11px]"):
                            self._word_count_label = ui.label("0 words")
                            self._save_status_label = ui.label("Saved").classes("text-emerald-400 font-medium")
                            self._width_toggle_btn = ui.button(
                                icon="open_in_full" if self._editor_width_mode == "centered" else "close_fullscreen",
                                on_click=self._toggle_editor_width,
                            ).props("flat round dense size=xs").classes("text-gray-400 hover:text-white")
                            with self._width_toggle_btn:
                                self._width_tooltip = ui.tooltip(
                                    "Switch to Full Width" if self._editor_width_mode == "centered" else "Switch to Centered Reading Width"
                                )

                    # Vditor Component Container
                    initial_content = ""
                    if self.state.active_chapter and self.state.active_chapter.path.exists():
                        initial_content = self.state.active_chapter.read_content()

                    with ui.column().classes("w-full flex-1 min-h-0 p-0 gap-0 overflow-hidden items-stretch"):
                        self.editor = VditorEditor(
                            initial_value=initial_content,
                            theme=self.state.theme,
                            width_mode=self._editor_width_mode,
                            on_save=self._handle_editor_save,
                            on_typing=self._handle_editor_typing,
                        )
                    self._update_word_count(initial_content)

                # 3. Right Inspector Column: Metadata or Git Panel (320px)
                self._right_panel_container = ui.column().classes(
                    "w-80 h-full border-l border-gray-800 bg-gray-900/40 flex-shrink-0 p-0 items-stretch overflow-hidden"
                )
                self._render_right_panel()

    def _render_right_panel(self) -> None:
        if not self._right_panel_container:
            return

        self._right_panel_container.clear()
        if not self._right_panel_visible:
            self._right_panel_container.set_visibility(False)
            return

        self._right_panel_container.set_visibility(True)
        with self._right_panel_container:
            if self._right_panel_tab == "metadata":
                self.metadata_panel = MetadataPanelComponent(self.state)
                self.metadata_panel.render()
            elif self._right_panel_tab == "git":
                self.git_panel = GitPanelComponent(self.state)
                self.git_panel.render()

    def _switch_right_tab(self, e) -> None:
        self._right_panel_tab = e.value
        self._right_panel_visible = True
        self._render_right_panel()

    def _toggle_right_panel(self) -> None:
        self._right_panel_visible = not self._right_panel_visible
        self._render_right_panel()

    def _toggle_editor_width(self) -> None:
        self._editor_width_mode = "full" if self._editor_width_mode == "centered" else "centered"
        if self.editor:
            self.editor.set_width_mode(self._editor_width_mode)
        if self._width_toggle_btn:
            new_icon = "close_fullscreen" if self._editor_width_mode == "full" else "open_in_full"
            new_tooltip = "Switch to Centered Reading Width" if self._editor_width_mode == "full" else "Switch to Full Width"
            self._width_toggle_btn.set_icon(new_icon)
            if self._width_tooltip:
                self._width_tooltip.set_text(new_tooltip)

    def _handle_chapter_selected(self, chapter: ChapterFile) -> None:
        if not chapter.path.exists():
            return

        content = chapter.read_content()
        if self._chapter_title_label:
            self._chapter_title_label.set_text(chapter.title)

        if self.editor:
            self.editor.set_content(content)

        self._update_word_count(content)
        if self._save_status_label:
            self._save_status_label.set_text("Saved")
            self._save_status_label.classes(replace="text-emerald-400")

    def _handle_editor_typing(self) -> None:
        if self._save_status_label:
            self._save_status_label.set_text("Saving...")
            self._save_status_label.classes(replace="text-amber-400")

    def _handle_editor_save(self, content: str) -> None:
        if self.state.active_chapter:
            self.state.active_chapter.write_content(content)
            self._update_word_count(content)
            if self._save_status_label:
                self._save_status_label.set_text("Saved")
                self._save_status_label.classes(replace="text-emerald-400")

            # Refresh git panel if visible
            if self.git_panel and self._right_panel_tab == "git":
                self.git_panel.render()

    def _update_word_count(self, content: str) -> None:
        words = len(content.split()) if content else 0
        if self._word_count_label:
            self._word_count_label.set_text(f"{words:,} words")

    async def _handle_manual_image_insert(self, event: events.UploadEventArguments, dialog: ui.dialog) -> None:
        ws = self.state.current_workspace
        if not ws or not self.editor:
            dialog.close()
            return

        try:
            file_obj = getattr(event, "file", None)
            if file_obj is not None:
                filename = getattr(file_obj, "name", "image.png")
                res = file_obj.read()
                file_bytes = await res if hasattr(res, "__await__") else res
            else:
                filename = getattr(event, "name", "image.png")
                content = getattr(event, "content", None)
                res = content.read() if content else b""
                file_bytes = await res if hasattr(res, "__await__") else res

            target_path = ws.save_asset(filename, file_bytes)

            # Append markdown image tag into active chapter
            img_md = f"\n\n![{target_path.name}](./assets/{target_path.name})\n"
            new_content = self.editor.content + img_md
            self.editor.set_content(new_content)
            dialog.close()
            try:
                ui.notify(f"Inserted image '{target_path.name}'", type="positive")
            except Exception:
                pass
        except Exception as err:
            try:
                ui.notify(f"Error inserting image: {err}", type="negative")
            except Exception:
                pass
        finally:
            if getattr(dialog, "value", False) or not getattr(dialog, "closed", True):
                try:
                    dialog.close()
                except Exception:
                    pass

    def _show_insert_image_dialog(self) -> None:
        """Display clean modal dialog to upload and insert image into chapter."""
        with ui.dialog() as dialog, ui.card().classes("w-96 p-5 gap-3"):
            ui.label("Insert Image into Chapter").classes("text-base font-semibold")
            ui.upload(
                on_upload=lambda e: self._handle_manual_image_insert(e, dialog),
                auto_upload=True,
                max_files=1,
            ).props('accept="image/*"').classes("w-full")
            with ui.row().classes("w-full justify-end mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
        dialog.open()

    def _show_export_dialog(self) -> None:
        """Display the export, compilation, and Kindle delivery dialog."""
        ws = self.state.current_workspace
        if not ws:
            return
        dialog = ExportDialog(workspace=ws, config_manager=self.state.config_manager)
        dialog.open()


