"""Dashboard view for browsing, opening, and creating ebook projects."""

import base64
from pathlib import Path
from typing import Any, Callable
from nicegui import ui

from ebook_editor.core.export.credentials import resolve_kindle_credentials
from ebook_editor.core.workspace import EbookWorkspace
from ebook_editor.ui.state import AppState

COVER_SIZE_CONFIGS: dict[str, dict[str, Any]] = {
    "small": {
        "width_px": 120,
        "height_px": 174,
        "font_size": "text-xs",
    },
    "medium": {
        "width_px": 150,
        "height_px": 218,
        "font_size": "text-sm",
    },
    "large": {
        "width_px": 185,
        "height_px": 268,
        "font_size": "text-base",
    },
}

COVER_GRADIENTS: list[str] = [
    "from-slate-900 via-indigo-950 to-slate-900 border-indigo-700/30",
    "from-slate-900 via-sky-950 to-slate-900 border-sky-700/30",
    "from-slate-900 via-teal-950 to-slate-900 border-teal-700/30",
    "from-slate-900 via-emerald-950 to-slate-900 border-emerald-700/30",
    "from-slate-900 via-amber-950 to-slate-900 border-amber-700/30",
    "from-slate-900 via-rose-950 to-slate-900 border-rose-700/30",
    "from-slate-900 via-purple-950 to-slate-900 border-purple-700/30",
]


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
        settings = self.state.config_manager.load_settings()
        cover_size = getattr(settings, "cover_size", "medium")
        cfg = COVER_SIZE_CONFIGS.get(cover_size, COVER_SIZE_CONFIGS["medium"])

        if self.container is None:
            self.container = ui.column().classes("w-full h-full flex-1 min-h-0 p-8 max-w-6xl mx-auto flex flex-col items-stretch overflow-hidden")
        else:
            self.container.clear()

        with self.container:
            # Header
            with ui.row().classes("w-full flex-shrink-0 items-center justify-between pb-5 border-b border-gray-700"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("menu_book", size="2.5rem").classes("text-indigo-400")
                    with ui.column().classes("gap-0"):
                        ui.label("Knowledge Master").classes("text-2xl font-bold")
                        ui.label("Local Markdown Ebook Studio").classes("text-sm text-gray-400")

                with ui.row().classes("items-center gap-3"):
                    ui.button(icon="settings", on_click=self._show_settings_dialog).props("outline round").classes("text-gray-300 hover:text-white").tooltip("Settings")
                    ui.button("Open Folder", icon="folder_open", on_click=self._show_open_dialog).props("outline")
                    ui.button("New Ebook", icon="add", on_click=self._show_create_dialog).classes("bg-indigo-600 hover:bg-indigo-700 text-white")

            # Two-tier horizontal bookshelf layout
            with ui.column().classes("w-full flex-1 min-h-0 mt-6 gap-6 items-stretch overflow-hidden"):
                # Tier 1: Recent Projects (Horizontal Shelf)
                with ui.column().classes("w-full flex-shrink-0 gap-3"):
                    ui.label("Recent Projects").classes("text-lg font-semibold text-gray-200")
                    self._render_recent_shelf(cfg)

                # Tier 2: Workspace Library (Full Height, Vertical Scrolling Grid)
                with ui.column().classes("w-full flex-1 min-h-0 gap-3 overflow-hidden"):
                    ui.label("Workspace Library").classes("text-lg font-semibold text-gray-200 flex-shrink-0")
                    self._render_discovered_grid(cfg)

    def _render_book_card(
        self,
        ws: EbookWorkspace,
        title: str,
        author: str,
        cfg: dict[str, Any],
        on_remove: Callable[[], None] | None = None,
    ) -> None:
        """Render a single front-facing book cover card with realistic spine and metadata."""
        cover_file = ws.assets_dir / "cover.png"
        has_custom_cover = False
        data_uri = ""

        if cover_file.is_file() and cover_file.stat().st_size > 100:
            try:
                raw_bytes = cover_file.read_bytes()
                b64 = base64.b64encode(raw_bytes).decode("ascii")
                data_uri = f"data:image/png;base64,{b64}"
                has_custom_cover = True
            except Exception:
                has_custom_cover = False

        card_w = cfg["width_px"]
        card_h = cfg["height_px"]

        with ui.column().classes("flex-shrink-0 group cursor-pointer select-none items-start gap-1.5").style(f"width: {card_w}px;").on("click", lambda _, w=ws: self.on_open_workspace(w)):
            # Front-facing book cover container
            with ui.element("div").classes(
                "relative rounded-r-md rounded-l-xs overflow-hidden shadow-lg border border-gray-700/60 "
                "group-hover:shadow-2xl group-hover:-translate-y-1.5 transition-all duration-300 w-full flex items-center justify-center bg-gray-900"
            ).style(f"height: {card_h}px;"):
                if has_custom_cover:
                    ui.image(data_uri).classes("w-full h-full object-cover")
                else:
                    grad_classes = COVER_GRADIENTS[abs(hash(title)) % len(COVER_GRADIENTS)]
                    with ui.column().classes(f"w-full h-full bg-gradient-to-br {grad_classes} p-3 flex flex-col justify-between items-center text-center"):
                        ui.icon("menu_book", size="1.6rem").classes("text-indigo-300/70 mt-1")
                        ui.label(title).classes("font-bold text-gray-100 line-clamp-3 leading-tight text-xs tracking-tight")
                        if author:
                            ui.label(author).classes("text-[10px] text-gray-400 truncate max-w-full font-medium tracking-wide")
                        else:
                            ui.element("div").classes("h-2")

                # Spine highlight / crease overlay (Left Edge)
                ui.element("div").classes(
                    "absolute top-0 left-0 w-3.5 h-full pointer-events-none z-10 "
                    "bg-gradient-to-r from-white/10 via-black/35 to-transparent border-r border-black/30"
                )

                # Hover-revealed remove button (for Recents)
                if on_remove:
                    ui.button(
                        icon="close",
                    ).props("flat round dense size=xs").classes(
                        "absolute top-1.5 right-1.5 z-20 bg-gray-900/80 hover:bg-red-600 text-gray-300 hover:text-white "
                        "opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    ).tooltip("Remove from recent").on("click.stop", lambda _: on_remove())

            # Title and Author text beneath the cover
            with ui.column().classes("w-full gap-0 pt-1 leading-tight"):
                lbl_title = ui.label(title).classes(f"w-full font-semibold {cfg['font_size']} text-gray-200 truncate group-hover:text-indigo-400 transition-colors")
                lbl_title.tooltip(title)
                if author:
                    ui.label(f"by {author}").classes("w-full text-xs text-gray-400 truncate")

    def _render_recent_shelf(self, cfg: dict[str, Any]) -> None:
        settings = self.state.config_manager.load_settings()
        recent_paths = settings.recent_ebooks

        if not recent_paths:
            with ui.card().classes("w-full p-4 text-center border border-dashed border-gray-700 bg-transparent"):
                ui.label("No recent ebooks opened yet.").classes("text-gray-400 text-sm")
            return

        with ui.row().classes("w-full overflow-x-auto overflow-y-hidden flex-nowrap gap-5 pb-3 items-start"):
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

                self._render_book_card(
                    ws=ws,
                    title=title,
                    author=author,
                    cfg=cfg,
                    on_remove=lambda ps=path_str: self._remove_recent(ps),
                )

    def _render_discovered_grid(self, cfg: dict[str, Any]) -> None:
        discovered = self.state.workspace_manager.discover_ebooks()
        if not discovered:
            with ui.card().classes("w-full p-6 text-center border border-dashed border-gray-700 bg-transparent"):
                ui.label(f"No ebooks found in {self.state.config_manager.ebooks_dir}").classes("text-gray-400 text-sm")
            return

        card_w = cfg["width_px"]
        with ui.element("div").classes(
            "w-full flex-1 min-h-0 overflow-y-auto pr-2 pb-8 grid gap-6"
        ).style(f"grid-template-columns: repeat(auto-fill, minmax({card_w}px, 1fr));"):
            for ws in discovered:
                title = ws.root.name
                author = ""
                try:
                    meta = ws.load_metadata()
                    title = meta.title
                    author = meta.author
                except Exception:
                    pass

                self._render_book_card(
                    ws=ws,
                    title=title,
                    author=author,
                    cfg=cfg,
                )

    def _remove_recent(self, path_str: str) -> None:
        self.state.config_manager.remove_recent_ebook(path_str)
        self.render()

    def _show_settings_dialog(self) -> None:
        settings = self.state.config_manager.load_settings()
        current_size = getattr(settings, "cover_size", "medium")
        creds = resolve_kindle_credentials(app_settings=settings)

        with ui.dialog() as dialog, ui.card().classes("w-[440px] p-6 gap-4 bg-gray-900 border border-gray-700 text-gray-200 select-none rounded-xl"):
            ui.label("Settings").classes("text-lg font-bold text-gray-100")

            # 1. Book Cover Size
            with ui.column().classes("w-full gap-2 border-b border-gray-800 pb-4"):
                ui.label("Book Cover Size").classes("text-xs font-semibold text-gray-300 uppercase tracking-wide")
                size_options = {
                    "small": "Small (120px)",
                    "medium": "Medium - Default (150px)",
                    "large": "Large (185px)",
                }
                size_radio = ui.radio(
                    options=size_options,
                    value=current_size,
                ).classes("gap-1 text-xs text-gray-300")

            # 2. Kindle & SMTP Delivery Settings
            with ui.column().classes("w-full gap-2"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Kindle & Email Delivery").classes("text-xs font-semibold text-gray-300 uppercase tracking-wide")
                    if creds.is_configured():
                        ui.badge("Configured", color="emerald").classes("text-[10px]")
                    else:
                        ui.badge("Incomplete", color="amber").classes("text-[10px]")

                ui.label("Credentials cascade from ~/.config/ebook-maker/.env when empty.").classes("text-[11px] text-gray-400 leading-tight")

                kindle_input = ui.input(
                    "Kindle Email",
                    value=settings.kindle_email or "",
                    placeholder=creds.kindle_email or "e.g. reader@kindle.com",
                ).classes("w-full text-xs")

                smtp_user_input = ui.input(
                    "SMTP User (Gmail)",
                    value=settings.smtp_user or "",
                    placeholder=creds.smtp_user or "e.g. author@gmail.com",
                ).classes("w-full text-xs")

                smtp_pass_input = ui.input(
                    "SMTP App Password",
                    value=settings.smtp_password or "",
                    placeholder="••••••••••••••••" if creds.smtp_password else "Gmail App Password",
                    password=True,
                    password_toggle_button=True,
                ).classes("w-full text-xs")

            def handle_save() -> None:
                new_size = size_radio.value
                self.state.config_manager.set_cover_size(new_size)

                # Update email settings
                updated_settings = self.state.config_manager.load_settings()
                updated_settings.cover_size = new_size
                updated_settings.kindle_email = kindle_input.value.strip() or None
                updated_settings.smtp_user = smtp_user_input.value.strip() or None
                updated_settings.smtp_password = smtp_pass_input.value.strip() or None
                self.state.config_manager.save_settings(updated_settings)

                dialog.close()
                ui.notify("Settings saved successfully", type="positive")
                self.render()

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Save", on_click=handle_save).classes("bg-indigo-600 text-white size=sm")

        dialog.open()

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
