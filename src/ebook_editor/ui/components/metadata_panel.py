"""Metadata and cover image configuration panel."""

import time
from nicegui import events, ui

from ebook_editor.core.models import EbookMetadata
from ebook_editor.ui.state import AppState


class MetadataPanelComponent:
    """Sidebar / inspector panel for viewing and modifying ebook metadata and cover."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self.container: ui.column | None = None
        self._cover_img_elem = None

    def render(self) -> None:
        """Render the metadata form and cover preview."""
        if self.container is None:
            self.container = ui.column().classes("w-full h-full p-4 gap-4 select-none overflow-y-auto")
        else:
            self.container.clear()
        ws = self.state.current_workspace
        if not ws:
            return

        try:
            meta = ws.load_metadata()
        except Exception as e:
            with self.container:
                ui.label(f"Error loading metadata: {e}").classes("text-red-400 text-xs")
            return

        with self.container:
            ui.label("Ebook Details").classes("text-sm font-bold uppercase tracking-wider text-gray-400 border-b border-gray-700/50 pb-2 w-full")

            # Cover Image Preview & Replacement
            with ui.column().classes("w-full items-center gap-2"):
                cover_filename = meta.cover_path.split("/")[-1] if meta.cover_path else "cover.png"
                cover_url = f"/api/workspace/assets/{cover_filename}?t={int(time.time())}"

                with ui.card().classes("p-1 bg-gray-800 border border-gray-700 shadow-md rounded overflow-hidden"):
                    self._cover_img_elem = ui.image(cover_url).classes("w-32 h-44 object-cover rounded")

                # Cover upload button
                ui.button("Change Cover", icon="image", on_click=self._show_cover_dialog).props("outline size=xs").classes("text-xs")

            # Form fields
            title_input = ui.input("Title", value=meta.title).classes("w-full text-xs")
            author_input = ui.input("Author", value=meta.author).classes("w-full text-xs")
            desc_input = ui.textarea("Description", value=meta.description).classes("w-full text-xs").props("rows=3")
            tags_input = ui.input("Tags (comma separated)", value=", ".join(meta.tags)).classes("w-full text-xs")

            def handle_save() -> None:
                new_title = title_input.value.strip()
                new_author = author_input.value.strip()
                if not new_title:
                    ui.notify("Title cannot be empty", type="warning")
                    return

                tag_list = [t.strip() for t in tags_input.value.split(",") if t.strip()]
                updated_meta = EbookMetadata(
                    title=new_title,
                    author=new_author,
                    description=desc_input.value.strip(),
                    cover_path=meta.cover_path or "assets/cover.png",
                    tags=tag_list,
                    created_at=meta.created_at,
                )
                ws.save_metadata(updated_meta)
                ui.notify("Metadata saved successfully", type="positive")

            with ui.row().classes("w-full justify-between items-center pt-2 border-t border-gray-700/50"):
                with ui.column().classes("gap-0"):
                    ui.label(f"Created: {meta.created_at.strftime('%Y-%m-%d')}").classes("text-[10px] text-gray-500")
                    ui.label(f"Updated: {meta.updated_at.strftime('%Y-%m-%d')}").classes("text-[10px] text-gray-500")

                ui.button("Save Details", icon="save", on_click=handle_save).classes("bg-indigo-600 text-white size=sm")

    def _handle_cover_upload(self, event: events.UploadEventArguments) -> None:
        ws = self.state.current_workspace
        if not ws:
            return

        file_bytes = event.content.read()
        ws.save_asset("cover.png", file_bytes)

        # Update metadata if needed
        try:
            meta = ws.load_metadata()
            meta.cover_path = "assets/cover.png"
            ws.save_metadata(meta)
        except Exception:
            pass

        ui.notify("Cover image updated!", type="positive")
        self.render()

    def _show_cover_dialog(self) -> None:
        """Display clean modal dialog to upload ebook cover."""
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3"):
            ui.label("Change Ebook Cover").classes("text-base font-semibold")
            ui.upload(
                on_upload=lambda e: (self._handle_cover_upload(e), dialog.close()),
                auto_upload=True,
                max_files=1,
            ).props('accept="image/*"').classes("w-full")
            with ui.row().classes("w-full justify-end mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
        dialog.open()

