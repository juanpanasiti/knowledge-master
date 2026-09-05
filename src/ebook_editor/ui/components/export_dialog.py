"""Modal dialog component for compiling EPUB, PDF, and sending to Kindle."""

import asyncio
from datetime import datetime
from pathlib import Path
from nicegui import ui

from ebook_editor.core.config import ConfigManager
from ebook_editor.core.export.credentials import resolve_kindle_credentials
from ebook_editor.core.export.exporter import (
    EbookExporter,
    get_epub_output_filename,
    get_pdf_output_filename,
)
from ebook_editor.core.export.sender import KindleSender
from ebook_editor.core.workspace import EbookWorkspace


class ExportDialog:
    """Provides an interactive modal dialog for exporting ebooks and sending to Kindle."""

    def __init__(
        self,
        workspace: EbookWorkspace,
        config_manager: ConfigManager,
    ) -> None:
        self.workspace = workspace
        self.config_manager = config_manager
        self.exporter = EbookExporter()
        self.dialog: ui.dialog | None = None
        self._epub_status_label = None
        self._pdf_status_label = None
        self._kindle_status_label = None
        self._filename_preview_label = None

    def _get_file_status(self, filename: str) -> str:
        """Return a human-readable file status and modification time."""
        file_path = self.workspace.dist_dir / filename
        if file_path.exists() and file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            return f"Built: {mtime} ({size_kb:.1f} KB)"
        return "Not generated yet"

    def open(self) -> None:
        """Open the export and publish dialog."""
        metadata = self.workspace.load_metadata()
        app_settings = self.config_manager.load_settings()
        creds = resolve_kindle_credentials(app_settings=app_settings)

        with ui.dialog() as dialog, ui.card().classes("w-[480px] p-6 gap-5 bg-gray-900 border border-gray-700 text-gray-200 select-none shadow-2xl rounded-xl"):
            self.dialog = dialog

            # Header
            with ui.row().classes("w-full justify-between items-start"):
                with ui.column().classes("gap-0"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("ios_share", size="1.4rem").classes("text-indigo-400")
                        ui.label("Export & Publish").classes("text-lg font-bold text-gray-100")
                    ui.label(metadata.title).classes("text-xs text-gray-400 truncate max-w-[360px]")

                ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm").classes("text-gray-400 hover:text-white")

            # Publication status toggle
            with ui.card().classes("w-full p-3 gap-2 bg-gray-800/60 border border-gray-700/50 rounded-lg"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.column().classes("gap-0"):
                        ui.label("Publication State").classes("text-xs font-semibold text-gray-200")
                        ui.label("Draft includes [DRAFT] prefix; Finished produces release filename.").classes("text-[11px] text-gray-400")

                    finished_switch = ui.switch(
                        "Finished",
                        value=metadata.finished,
                    ).props("dense size=sm").classes("text-xs text-indigo-400")

                epub_name = get_epub_output_filename(metadata)
                pdf_name = get_pdf_output_filename(metadata)
                self._filename_preview_label = ui.label(f"Output files: {epub_name} | {pdf_name}").classes("text-[11px] font-mono text-indigo-300 truncate w-full")

                def handle_switch_change(e) -> None:
                    metadata.finished = bool(e.value)
                    self.workspace.save_metadata(metadata)
                    new_epub = get_epub_output_filename(metadata)
                    new_pdf = get_pdf_output_filename(metadata)
                    if self._filename_preview_label:
                        self._filename_preview_label.set_text(f"Output files: {new_epub} | {new_pdf}")
                    if self._epub_status_label:
                        self._epub_status_label.set_text(self._get_file_status(new_epub))
                    if self._pdf_status_label:
                        self._pdf_status_label.set_text(self._get_file_status(new_pdf))

                finished_switch.on_value_change(handle_switch_change)

            # Export Actions Grid
            with ui.column().classes("w-full gap-3"):
                # 1. EPUB Export Row
                with ui.card().classes("w-full p-3 bg-gray-800/40 border border-gray-700/40 rounded-lg"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2.5"):
                            ui.icon("book", size="1.2rem").classes("text-indigo-400")
                            with ui.column().classes("gap-0"):
                                ui.label("EPUB Document").classes("text-xs font-semibold text-gray-200")
                                self._epub_status_label = ui.label(self._get_file_status(epub_name)).classes("text-[11px] text-gray-400")

                        epub_spinner = ui.spinner(size="sm").classes("text-indigo-400")
                        epub_spinner.set_visibility(False)

                        epub_btn = ui.button(
                            "Generate EPUB",
                            icon="auto_awesome",
                        ).props("size=sm dense").classes("bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3")

                        async def handle_generate_epub() -> None:
                            epub_btn.disable()
                            epub_spinner.set_visibility(True)
                            try:
                                result_path = await asyncio.to_thread(self.exporter.compile_epub, self.workspace)
                                ui.notify(f"EPUB generated successfully: {result_path.name}", type="positive")
                                if self._epub_status_label:
                                    self._epub_status_label.set_text(self._get_file_status(result_path.name))
                            except Exception as err:
                                ui.notify(f"EPUB export failed: {err}", type="negative")
                            finally:
                                epub_btn.enable()
                                epub_spinner.set_visibility(False)

                        epub_btn.on_click(handle_generate_epub)

                # 2. PDF Export Row
                with ui.card().classes("w-full p-3 bg-gray-800/40 border border-gray-700/40 rounded-lg"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2.5"):
                            ui.icon("picture_as_pdf", size="1.2rem").classes("text-purple-400")
                            with ui.column().classes("gap-0"):
                                ui.label("A4 PDF Document").classes("text-xs font-semibold text-gray-200")
                                self._pdf_status_label = ui.label(self._get_file_status(pdf_name)).classes("text-[11px] text-gray-400")

                        pdf_spinner = ui.spinner(size="sm").classes("text-purple-400")
                        pdf_spinner.set_visibility(False)

                        pdf_btn = ui.button(
                            "Generate PDF",
                            icon="auto_awesome",
                        ).props("size=sm dense").classes("bg-purple-600 hover:bg-purple-500 text-white text-xs px-3")

                        async def handle_generate_pdf() -> None:
                            pdf_btn.disable()
                            pdf_spinner.set_visibility(True)
                            try:
                                result_path = await asyncio.to_thread(self.exporter.compile_pdf, self.workspace)
                                ui.notify(f"PDF generated successfully: {result_path.name}", type="positive")
                                if self._pdf_status_label:
                                    self._pdf_status_label.set_text(self._get_file_status(result_path.name))
                            except Exception as err:
                                ui.notify(f"PDF export failed: {err}", type="negative")
                            finally:
                                pdf_btn.enable()
                                pdf_spinner.set_visibility(False)

                        pdf_btn.on_click(handle_generate_pdf)

                # 3. Kindle Transmission Row
                with ui.card().classes("w-full p-3 bg-gray-800/40 border border-gray-700/40 rounded-lg"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2.5"):
                            ui.icon("send_to_mobile", size="1.2rem").classes("text-amber-400")
                            with ui.column().classes("gap-0"):
                                ui.label("Send to Kindle").classes("text-xs font-semibold text-gray-200")
                                target_text = f"To: {creds.kindle_email}" if creds.kindle_email else "No Kindle email configured"
                                self._kindle_status_label = ui.label(target_text).classes("text-[11px] text-gray-400")

                        kindle_spinner = ui.spinner(size="sm").classes("text-amber-400")
                        kindle_spinner.set_visibility(False)

                        kindle_btn = ui.button(
                            "Send EPUB",
                            icon="send",
                        ).props("size=sm dense").classes("bg-amber-600 hover:bg-amber-500 text-white text-xs px-3")

                        async def handle_send_kindle() -> None:
                            active_creds = resolve_kindle_credentials(self.config_manager.load_settings())
                            if not active_creds.is_configured():
                                missing = ", ".join(active_creds.missing_fields())
                                ui.notify(f"Missing Kindle credentials ({missing}). Check Settings or .env", type="warning")
                                return

                            kindle_btn.disable()
                            kindle_spinner.set_visibility(True)
                            try:
                                # Ensure EPUB exists
                                cur_meta = self.workspace.load_metadata()
                                target_epub_name = get_epub_output_filename(cur_meta)
                                epub_path = self.workspace.dist_dir / target_epub_name
                                if not epub_path.exists():
                                    ui.notify("Compiling latest EPUB before transmission...", type="info")
                                    epub_path = await asyncio.to_thread(self.exporter.compile_epub, self.workspace)
                                    if self._epub_status_label:
                                        self._epub_status_label.set_text(self._get_file_status(epub_path.name))

                                sender = KindleSender(active_creds)
                                await asyncio.to_thread(sender.send_epub, epub_path)
                                ui.notify(f"EPUB successfully sent to {active_creds.kindle_email}!", type="positive")
                            except Exception as err:
                                ui.notify(f"Kindle delivery failed: {err}", type="negative")
                            finally:
                                kindle_btn.enable()
                                kindle_spinner.set_visibility(False)

                        kindle_btn.on_click(handle_send_kindle)

            # Footer: destination note and close button
            with ui.row().classes("w-full justify-between items-center pt-2 border-t border-gray-700/50"):
                ui.label(f"Folder: dist/").classes("text-[10px] text-gray-500 font-mono")
                ui.button("Done", on_click=dialog.close).props("flat size=sm").classes("text-gray-300 hover:text-white")

        dialog.open()
