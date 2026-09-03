"""Knowledge Master - Main Application Entrypoint."""

import argparse
import sys
from pathlib import Path
from nicegui import app, ui

from ebook_editor.core.asset_server import register_asset_routes
from ebook_editor.core.workspace import EbookWorkspace
from ebook_editor.ui.dashboard import DashboardView
from ebook_editor.ui.state import AppState
from ebook_editor.ui.workspace_view import WorkspaceView
from ebook_editor.ui.components.editor import VDITOR_HEAD_HTML


GLOBAL_STYLES = """
<style>
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow: hidden !important;
  }
  .q-page, .nicegui-content {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    width: 100% !important;
    overflow: hidden !important;
  }
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(156, 163, 175, 0.3);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(156, 163, 175, 0.5);
  }
</style>
"""


def setup_app(initial_ebook_path: str | None = None) -> AppState:
    """Configure UI layout, routes, and views."""
    state = AppState()

    # Register dynamic asset serving for the active ebook
    register_asset_routes(app, lambda: state.current_workspace)

    @ui.page("/")
    def index_page():
        ui.add_head_html(GLOBAL_STYLES)
        ui.add_head_html(VDITOR_HEAD_HTML)
        ui.dark_mode(value=(state.theme == "dark"))
        root_container = ui.column().classes("w-full h-full p-0 m-0 gap-0 overflow-hidden bg-gray-950 text-gray-100 items-stretch")

        dashboard_view: DashboardView | None = None
        workspace_view: WorkspaceView | None = None

        def show_dashboard() -> None:
            nonlocal dashboard_view, workspace_view
            root_container.clear()
            state.set_active_workspace(None)
            with root_container:
                dashboard_view = DashboardView(state, on_open_workspace=show_workspace)
                dashboard_view.render()

        def show_workspace(workspace: EbookWorkspace) -> None:
            nonlocal dashboard_view, workspace_view
            root_container.clear()
            state.set_active_workspace(workspace)
            with root_container:
                workspace_view = WorkspaceView(state, on_back_to_dashboard=show_dashboard)
                workspace_view.render()
                if workspace_view.editor:
                    ui.timer(0.1, workspace_view.editor.init_editor, once=True)

        if initial_ebook_path:
            p = Path(initial_ebook_path).expanduser().resolve()
            if p.is_dir():
                try:
                    ws = state.workspace_manager.open_ebook(p)
                    show_workspace(ws)
                    return
                except Exception as e:
                    ui.notify(f"Could not open initial ebook: {e}", type="negative")

        show_dashboard()

    return state


def run() -> None:
    """Entrypoint invoked by CLI command 'knowledge-master'."""
    parser = argparse.ArgumentParser(description="Knowledge Master - Local Ebook Editor")
    parser.add_argument("path", nargs="?", help="Optional path to an ebook directory to open")
    parser.add_argument("--browser", action="store_true", help="Open in standard web browser instead of native desktop window")
    parser.add_argument("--port", type=int, default=None, help="Custom server port")
    args = parser.parse_args()

    state = setup_app(initial_ebook_path=args.path)
    use_native = not args.browser

    # Launch NiceGUI
    try:
        ui.run(
            native=use_native,
            window_size=(state.config_manager.load_settings().window_width, state.config_manager.load_settings().window_height),
            title="Knowledge Master",
            reload=False,
            port=args.port,
        )
    except Exception as e:
        if use_native:
            print(f"\n[Warning] Failed to start native desktop window ({e}).")
            print("Falling back to standard browser mode...\n")
            ui.run(
                native=False,
                title="Knowledge Master",
                reload=False,
                port=args.port,
            )
        else:
            raise


if __name__ in {"__main__", "__mp_main__"}:
    run()
