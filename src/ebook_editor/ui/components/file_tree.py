"""Sidebar multi-folder accordion explorer component for content, resources, assets, and dist."""

from pathlib import Path
from typing import Callable
from nicegui import events, ui

from ebook_editor.core.workspace import ChapterFile, EbookWorkspace, WorkspaceFile
from ebook_editor.ui.state import AppState


def _format_size(size_bytes: int) -> str:
    """Format byte size into human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


class FileTreeComponent:
    """Multi-folder accordion file explorer displaying Content, Resources, Assets, and Dist."""

    def __init__(
        self,
        state: AppState,
        on_select_chapter: Callable[[WorkspaceFile], None],
    ) -> None:
        self.state = state
        self.on_select_chapter = on_select_chapter
        self.container: ui.column | None = None
        self._file_elements: dict[str, ui.element] = {}
        self._expanded_sections: set[str] = set()

    def render(self) -> None:
        """Render the multi-folder accordion explorer sidebar."""
        self._file_elements.clear()
        if self.container is None:
            self.container = ui.column().classes(
                "w-full h-full flex-1 min-h-0 flex flex-col p-2 gap-2 select-none items-stretch overflow-hidden"
            )
        else:
            self.container.clear()

        ws = self.state.current_workspace
        if not ws:
            return

        slug = ws.root.name
        saved_expanded = self.state.config_manager.get_explorer_expanded_sections(slug)
        self._expanded_sections = set(saved_expanded)

        with self.container:
            with ui.column().classes("w-full flex-1 min-h-0 overflow-y-auto gap-2 p-0 items-stretch"):
                self._render_content_section(ws)
                self._render_resources_section(ws)
                self._render_assets_section(ws)
                self._render_dist_section(ws)

    def _handle_expansion_change(self, section: str, is_open: bool) -> None:
        """Update and persist expanded accordion sections."""
        if is_open:
            self._expanded_sections.add(section)
        else:
            self._expanded_sections.discard(section)

        ws = self.state.current_workspace
        if ws:
            slug = ws.root.name
            self.state.config_manager.set_explorer_expanded_sections(slug, list(self._expanded_sections))

    # ==========================================
    # 1. CONTENT SECTION
    # ==========================================
    def _render_content_section(self, ws: EbookWorkspace) -> None:
        content_files = ws.list_content_files()
        is_expanded = "content" in self._expanded_sections

        with ui.expansion(
            value=is_expanded,
            on_value_change=lambda e: self._handle_expansion_change("content", e.value),
        ).props("dense header-class='px-2 py-1 rounded hover:bg-gray-800/60 text-xs font-semibold text-gray-300'").classes("w-full bg-gray-900/40 rounded border border-gray-800/50") as exp:
            with exp.add_slot("header"):
                with ui.row().classes("flex-1 items-center justify-between pr-2"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("article", size="1rem").classes("text-indigo-400")
                        ui.label("Content").classes("text-xs font-semibold uppercase tracking-wider text-gray-300")
                        ui.badge(str(len(content_files)), color="indigo-900").props("dense rounded text-color=indigo-200").classes("text-[10px] px-1.5 py-0")

                    ui.button(
                        icon="add",
                    ).props("round flat dense size=xs").classes("text-indigo-400 hover:text-white").tooltip("New Content File").on(
                        "click",
                        lambda: self._show_new_file_dialog("content"),
                        js_handler="(e) => { e.stopPropagation(); emit(); }",
                    )

            with ui.column().classes("w-full p-1 gap-1 items-stretch"):
                if not content_files:
                    ui.label("No content files yet.").classes("text-[11px] text-gray-500 italic p-2 text-center")
                else:
                    for cf in content_files:
                        self._render_text_file_item(cf)

    # ==========================================
    # 2. RESOURCES SECTION
    # ==========================================
    def _render_resources_section(self, ws: EbookWorkspace) -> None:
        resource_files = ws.list_resource_files()
        is_expanded = "resources" in self._expanded_sections

        with ui.expansion(
            value=is_expanded,
            on_value_change=lambda e: self._handle_expansion_change("resources", e.value),
        ).props("dense header-class='px-2 py-1 rounded hover:bg-gray-800/60 text-xs font-semibold text-gray-300'").classes("w-full bg-gray-900/40 rounded border border-gray-800/50") as exp:
            with exp.add_slot("header"):
                with ui.row().classes("flex-1 items-center justify-between pr-2"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("lightbulb", size="1rem").classes("text-amber-400")
                        ui.label("Resources").classes("text-xs font-semibold uppercase tracking-wider text-gray-300")
                        ui.badge(str(len(resource_files)), color="amber-950").props("dense rounded text-color=amber-300").classes("text-[10px] px-1.5 py-0")

                    ui.button(
                        icon="add",
                    ).props("round flat dense size=xs").classes("text-amber-400 hover:text-white").tooltip("New Resource File (.mmd, .md, .txt)").on(
                        "click",
                        lambda: self._show_new_file_dialog("resources"),
                        js_handler="(e) => { e.stopPropagation(); emit(); }",
                    )

            with ui.column().classes("w-full p-1 gap-1 items-stretch"):
                if not resource_files:
                    ui.label("No supplementary resources.").classes("text-[11px] text-gray-500 italic p-2 text-center")
                else:
                    for rf in resource_files:
                        self._render_text_file_item(rf)

    # ==========================================
    # 3. ASSETS SECTION
    # ==========================================
    def _render_assets_section(self, ws: EbookWorkspace) -> None:
        asset_files = ws.list_asset_files()
        is_expanded = "assets" in self._expanded_sections

        with ui.expansion(
            value=is_expanded,
            on_value_change=lambda e: self._handle_expansion_change("assets", e.value),
        ).props("dense header-class='px-2 py-1 rounded hover:bg-gray-800/60 text-xs font-semibold text-gray-300'").classes("w-full bg-gray-900/40 rounded border border-gray-800/50") as exp:
            with exp.add_slot("header"):
                with ui.row().classes("flex-1 items-center justify-between pr-2"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("image", size="1rem").classes("text-emerald-400")
                        ui.label("Assets").classes("text-xs font-semibold uppercase tracking-wider text-gray-300")
                        ui.badge(str(len(asset_files)), color="emerald-950").props("dense rounded text-color=emerald-300").classes("text-[10px] px-1.5 py-0")

                    ui.button(
                        icon="file_upload",
                    ).props("round flat dense size=xs").classes("text-emerald-400 hover:text-white").tooltip("Upload Image Asset").on(
                        "click",
                        self._show_upload_asset_dialog,
                        js_handler="(e) => { e.stopPropagation(); emit(); }",
                    )

            with ui.column().classes("w-full p-1 gap-1 items-stretch"):
                if not asset_files:
                    ui.label("No assets yet.").classes("text-[11px] text-gray-500 italic p-2 text-center")
                else:
                    for af in asset_files:
                        self._render_asset_item(af)

    # ==========================================
    # 4. DIST SECTION
    # ==========================================
    def _render_dist_section(self, ws: EbookWorkspace) -> None:
        dist_files = ws.list_dist_files()
        is_expanded = "dist" in self._expanded_sections

        with ui.expansion(
            value=is_expanded,
            on_value_change=lambda e: self._handle_expansion_change("dist", e.value),
        ).props("dense header-class='px-2 py-1 rounded hover:bg-gray-800/60 text-xs font-semibold text-gray-300'").classes("w-full bg-gray-900/40 rounded border border-gray-800/50") as exp:
            with exp.add_slot("header"):
                with ui.row().classes("flex-1 items-center justify-between pr-2"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("inventory_2", size="1rem").classes("text-purple-400")
                        ui.label("Dist").classes("text-xs font-semibold uppercase tracking-wider text-gray-300")
                        ui.badge(str(len(dist_files)), color="purple-950").props("dense rounded text-color=purple-300").classes("text-[10px] px-1.5 py-0")

            with ui.column().classes("w-full p-1 gap-1 items-stretch"):
                if not dist_files:
                    ui.label("No compiled builds yet.").classes("text-[11px] text-gray-500 italic p-2 text-center")
                else:
                    for df in dist_files:
                        self._render_dist_item(df)

    # ==========================================
    # ITEM RENDERERS
    # ==========================================
    def _render_text_file_item(self, file_item: WorkspaceFile) -> None:
        key = f"{file_item.category}:{file_item.name}"
        is_active = (
            self.state.active_file is not None
            and self.state.active_file.name == file_item.name
            and getattr(self.state.active_file, "category", "content") == file_item.category
        )

        active_classes = "bg-indigo-600/30 text-indigo-300 font-medium border-l-2 border-indigo-500"
        inactive_classes = "text-gray-300 hover:bg-gray-800/80 hover:text-gray-100"
        base_classes = "w-full px-2 py-1 rounded flex flex-row items-center justify-between text-xs cursor-pointer transition-colors group "
        current_classes = base_classes + (active_classes if is_active else inactive_classes)

        item_elem = ui.element("div").classes(current_classes)
        self._file_elements[key] = item_elem

        # Determine icon based on category and extension
        if file_item.category == "resources":
            if file_item.name.lower().endswith((".mmd", ".mermaid")):
                icon_name = "account_tree"
                icon_color = "text-cyan-400"
            else:
                icon_name = "description"
                icon_color = "text-amber-300"
            display_title = file_item.name
        else:
            icon_name = "description"
            icon_color = "text-gray-400 group-hover:text-indigo-300"
            display_title = file_item.title

        with item_elem:
            with ui.row().classes("items-center gap-2 flex-grow truncate").on(
                "click", lambda _, fi=file_item: self._handle_select_file(fi)
            ):
                ui.icon(icon_name, size="0.9rem").classes(f"{icon_color} flex-shrink-0")
                ui.label(display_title).classes("truncate")

            with ui.button(icon="more_vert").props("flat round dense size=xs").classes(
                "opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition-opacity"
            ).tooltip("File options"):
                with ui.menu().classes("bg-gray-800 text-white border border-gray-700"):
                    ui.menu_item("Rename", on_click=lambda _, fi=file_item: self._show_rename_dialog(fi))
                    ui.menu_item("Delete", on_click=lambda _, fi=file_item: self._show_delete_dialog(fi)).classes(
                        "text-red-400 hover:bg-red-950/40"
                    )

    def _render_asset_item(self, asset_path: Path) -> None:
        with ui.row().classes(
            "w-full px-2 py-1 rounded flex flex-row items-center justify-between text-xs text-gray-300 hover:bg-gray-800/80 hover:text-gray-100 cursor-pointer transition-colors group"
        ):
            with ui.row().classes("items-center gap-2 flex-grow truncate").on(
                "click", lambda _, ap=asset_path: self._show_asset_preview_dialog(ap)
            ):
                ui.icon("image", size="0.9rem").classes("text-emerald-400 flex-shrink-0")
                ui.label(asset_path.name).classes("truncate")

            with ui.button(icon="more_vert").props("flat round dense size=xs").classes(
                "opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition-opacity"
            ).tooltip("Asset options"):
                with ui.menu().classes("bg-gray-800 text-white border border-gray-700"):
                    ui.menu_item("Preview", on_click=lambda _, ap=asset_path: self._show_asset_preview_dialog(ap))
                    ui.menu_item(
                        "Copy Markdown Link",
                        on_click=lambda _, ap=asset_path: self._copy_markdown_link(ap),
                    )
                    ui.menu_item(
                        "Delete",
                        on_click=lambda _, ap=asset_path: self._delete_asset(ap),
                    ).classes("text-red-400 hover:bg-red-950/40")

    def _render_dist_item(self, dist_path: Path) -> None:
        is_pdf = dist_path.suffix.lower() == ".pdf"
        icon_name = "picture_as_pdf" if is_pdf else "menu_book"
        icon_color = "text-red-400" if is_pdf else "text-purple-400"

        size_str = ""
        try:
            size_str = _format_size(dist_path.stat().st_size)
        except Exception:
            pass

        with ui.row().classes(
            "w-full px-2 py-1 rounded flex flex-row items-center justify-between text-xs text-gray-300 hover:bg-gray-800/80 hover:text-gray-100 cursor-pointer transition-colors group"
        ):
            with ui.row().classes("items-center gap-2 flex-grow truncate").on(
                "click", lambda _, dp=dist_path: self._handle_dist_click(dp)
            ):
                ui.icon(icon_name, size="0.9rem").classes(f"{icon_color} flex-shrink-0")
                ui.label(dist_path.name).classes("truncate")
                if size_str:
                    ui.label(size_str).classes("text-[10px] text-gray-500 ml-auto mr-1")

            with ui.button(icon="more_vert").props("flat round dense size=xs").classes(
                "opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white transition-opacity"
            ).tooltip("Build options"):
                with ui.menu().classes("bg-gray-800 text-white border border-gray-700"):
                    ui.menu_item(
                        "View / Open" if is_pdf else "Download",
                        on_click=lambda _, dp=dist_path: self._handle_dist_click(dp),
                    )
                    ui.menu_item(
                        "Delete",
                        on_click=lambda _, dp=dist_path: self._delete_dist(dp),
                    ).classes("text-red-400 hover:bg-red-950/40")

    # ==========================================
    # FILE ACTIONS & SELECTION
    # ==========================================
    def _handle_select_file(self, file_item: WorkspaceFile) -> None:
        self.state.set_active_file(file_item)
        active_classes = "bg-indigo-600/30 text-indigo-300 font-medium border-l-2 border-indigo-500"
        inactive_classes = "text-gray-300 hover:bg-gray-800/80 hover:text-gray-100"
        target_key = f"{file_item.category}:{file_item.name}"

        for k, elem in self._file_elements.items():
            if k == target_key:
                elem.classes(remove=inactive_classes, add=active_classes)
            else:
                elem.classes(remove=active_classes, add=inactive_classes)

        self.on_select_chapter(file_item)

    def _show_new_file_dialog(self, category: str) -> None:
        title_text = "New Content Chapter" if category == "content" else "New Resource File"
        placeholder_text = "e.g. 02 - Core Concepts" if category == "content" else "e.g. flowchart.mmd, notes.md"

        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3 bg-gray-900 border border-gray-800 text-white"):
            ui.label(title_text).classes("text-base font-semibold")
            name_input = ui.input("Filename or Title", placeholder=placeholder_text).classes("w-full")

            def handle_create() -> None:
                val = name_input.value.strip()
                if not val:
                    ui.notify("Name cannot be empty", type="warning")
                    return
                dialog.close()
                ws = self.state.current_workspace
                if not ws:
                    return

                try:
                    if category == "content":
                        new_f = ws.create_chapter(val, f"# {val}\n\n")
                    else:
                        init_content = "graph TD;\n    A-->B;\n" if val.endswith((".mmd", ".mermaid")) else f"# {val}\n\n"
                        new_f = ws.create_resource(val, init_content)

                    self.state.set_active_file(new_f)
                    ui.notify(f"Created '{new_f.name}'", type="positive")
                    self.render()
                    self.on_select_chapter(new_f)
                except Exception as e:
                    ui.notify(str(e), type="negative")

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Create", on_click=handle_create).classes("bg-indigo-600 text-white size=sm")

        dialog.open()

    def _show_rename_dialog(self, file_item: WorkspaceFile) -> None:
        init_val = file_item.title if file_item.category == "content" else file_item.name
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3 bg-gray-900 border border-gray-800 text-white"):
            ui.label(f"Rename {file_item.category.capitalize()} File").classes("text-base font-semibold")
            name_input = ui.input("New Name", value=init_val).classes("w-full")

            def handle_rename() -> None:
                val = name_input.value.strip()
                if not val or val == init_val:
                    dialog.close()
                    return
                dialog.close()
                ws = self.state.current_workspace
                if not ws:
                    return

                try:
                    if file_item.category == "content":
                        renamed = ws.rename_chapter(file_item.name, val)
                    else:
                        renamed = ws.rename_resource(file_item.name, val)

                    if (
                        self.state.active_file
                        and self.state.active_file.name == file_item.name
                        and getattr(self.state.active_file, "category", "content") == file_item.category
                    ):
                        self.state.set_active_file(renamed)
                        self.on_select_chapter(renamed)

                    ui.notify(f"Renamed to '{renamed.name}'", type="positive")
                    self.render()
                except Exception as e:
                    ui.notify(str(e), type="negative")

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Rename", on_click=handle_rename).classes("bg-indigo-600 text-white size=sm")

        dialog.open()

    def _show_delete_dialog(self, file_item: WorkspaceFile) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-80 p-5 gap-3 bg-gray-900 border border-gray-800 text-white"):
            ui.label(f"Delete {file_item.category.capitalize()} File?").classes("text-base font-semibold text-red-400")
            ui.label(f"Are you sure you want to delete '{file_item.name}'? This cannot be undone.").classes("text-xs text-gray-300")

            def handle_delete() -> None:
                dialog.close()
                ws = self.state.current_workspace
                if not ws:
                    return

                if file_item.category == "content":
                    ws.delete_chapter(file_item.name)
                    remaining = ws.list_content_files()
                else:
                    ws.delete_resource(file_item.name)
                    remaining = ws.list_resource_files()

                if (
                    self.state.active_file
                    and self.state.active_file.name == file_item.name
                    and getattr(self.state.active_file, "category", "content") == file_item.category
                ):
                    next_file = remaining[0] if remaining else None
                    self.state.set_active_file(next_file)
                    if next_file:
                        self.on_select_chapter(next_file)

                ui.notify(f"Deleted '{file_item.name}'", type="info")
                self.render()

            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat size=sm")
                ui.button("Delete", on_click=handle_delete).classes("bg-red-600 text-white size=sm")

        dialog.open()

    # ==========================================
    # ASSET ACTIONS & MODAL PREVIEW
    # ==========================================
    def _show_asset_preview_dialog(self, asset_path: Path) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-[480px] p-4 gap-3 bg-gray-900 border border-gray-800 text-white shadow-2xl"):
            with ui.row().classes("w-full justify-between items-center pb-2 border-b border-gray-800"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("image", size="1.2rem").classes("text-emerald-400")
                    ui.label(asset_path.name).classes("font-semibold text-sm truncate max-w-[320px]")
                ui.button(icon="close", on_click=dialog.close).props("flat round dense size=xs").classes("text-gray-400 hover:text-white")

            # Image Preview Frame
            with ui.column().classes("w-full max-h-72 items-center justify-center bg-gray-950/80 rounded p-2 overflow-hidden border border-gray-800/60"):
                ui.image(f"/assets/{asset_path.name}").classes("max-h-64 object-contain rounded")

            # File info
            size_str = ""
            try:
                size_str = _format_size(asset_path.stat().st_size)
            except Exception:
                pass

            with ui.row().classes("w-full justify-between items-center text-xs text-gray-400 pt-1"):
                ui.label(f"Path: assets/{asset_path.name}").classes("truncate")
                if size_str:
                    ui.label(size_str)

            # Actions
            with ui.row().classes("w-full justify-between items-center pt-2 border-t border-gray-800"):
                ui.button(
                    "Delete",
                    icon="delete",
                    on_click=lambda: (dialog.close(), self._delete_asset(asset_path)),
                ).props("flat dense size=sm").classes("text-red-400 hover:bg-red-950/40")

                with ui.row().classes("gap-2"):
                    ui.button(
                        "Copy Markdown Link",
                        icon="content_copy",
                        on_click=lambda: self._copy_markdown_link(asset_path),
                    ).classes("bg-indigo-600 hover:bg-indigo-700 text-white size=sm").tooltip("Copy ![name](assets/...) to clipboard")

        dialog.open()

    def _copy_markdown_link(self, asset_path: Path) -> None:
        link_md = f"![{asset_path.stem}](./assets/{asset_path.name})"
        ui.run_javascript(f"navigator.clipboard.writeText({repr(link_md)})")
        ui.notify(f"Copied Markdown link: {link_md}", type="positive")

    def _show_upload_asset_dialog(self) -> None:
        ws = self.state.current_workspace
        if not ws:
            return

        with ui.dialog() as dialog, ui.card().classes("w-96 p-5 gap-3 bg-gray-900 border border-gray-800 text-white"):
            ui.label("Upload Asset").classes("text-base font-semibold")

            async def handle_upload(e: events.UploadEventArguments) -> None:
                try:
                    file_obj = getattr(e, "file", None)
                    if file_obj is not None:
                        filename = getattr(file_obj, "name", "asset.png")
                        res = file_obj.read()
                        file_bytes = await res if hasattr(res, "__await__") else res
                    else:
                        filename = getattr(e, "name", "asset.png")
                        content = getattr(e, "content", None)
                        res = content.read() if content else b""
                        file_bytes = await res if hasattr(res, "__await__") else res

                    ws.save_asset(filename, file_bytes)
                    dialog.close()
                    ui.notify(f"Uploaded asset '{filename}'", type="positive")
                    self.render()
                except Exception as err:
                    ui.notify(f"Upload failed: {err}", type="negative")

            ui.upload(
                on_upload=handle_upload,
                auto_upload=True,
                max_files=5,
            ).props('accept="image/*"').classes("w-full")

            with ui.row().classes("w-full justify-end mt-2"):
                ui.button("Close", on_click=dialog.close).props("flat size=sm")

        dialog.open()

    def _delete_asset(self, asset_path: Path) -> None:
        ws = self.state.current_workspace
        if ws:
            ws.delete_asset(asset_path.name)
            ui.notify(f"Deleted asset '{asset_path.name}'", type="info")
            self.render()

    # ==========================================
    # DIST ACTIONS
    # ==========================================
    def _handle_dist_click(self, dist_path: Path) -> None:
        if dist_path.suffix.lower() == ".pdf":
            ui.navigate.to(f"/api/workspace/dist/{dist_path.name}", new_tab=True)
            ui.notify(f"Opening '{dist_path.name}' in new tab", type="positive")
        else:
            ui.download(f"/api/workspace/dist/{dist_path.name}", dist_path.name)
            ui.notify(f"Downloading '{dist_path.name}'", type="positive")

    def _delete_dist(self, dist_path: Path) -> None:
        ws = self.state.current_workspace
        if ws:
            ws.delete_dist(dist_path.name)
            self.render()
            ui.notify(f"Deleted build '{dist_path.name}'", type="info")
