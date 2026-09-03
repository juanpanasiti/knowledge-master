"""Git version control panel component with graceful degradation."""

from nicegui import ui

from ebook_editor.core.git_service import GitService
from ebook_editor.ui.state import AppState


class GitPanelComponent:
    """Sidebar / tab panel for inspecting git status, staging, committing, and logs."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self.container: ui.column | None = None

    def render(self) -> None:
        """Render the complete Git panel view."""
        if self.container is None:
            self.container = ui.column().classes("w-full h-full p-4 gap-4 select-none overflow-y-auto")
        else:
            self.container.clear()
        ws = self.state.current_workspace
        if not ws:
            return

        git_svc = self.state.git_service or GitService(ws.root)
        status = git_svc.get_status()

        with self.container:
            # Header
            with ui.row().classes("w-full items-center justify-between border-b border-gray-700/50 pb-2"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("commit", size="1.2rem").classes("text-indigo-400")
                    ui.label("Source Control").classes("text-sm font-bold uppercase tracking-wider text-gray-400")

                ui.button(icon="refresh", on_click=self.render).props("flat round dense size=xs").classes("text-gray-400 hover:text-white").tooltip("Refresh status")

            # 1. Graceful degradation: Git not installed
            if not status.is_git_available:
                with ui.card().classes("w-full p-3 bg-amber-950/30 border border-amber-800/50 text-amber-200 text-xs gap-1"):
                    ui.label("Git Unavailable").classes("font-bold")
                    ui.label(status.error_message or "Git is not installed on this system.")
                    ui.label("All other editor features continue to work normally.").classes("text-[10px] text-amber-300/80")
                return

            # 2. Not a Git repository yet
            if not status.is_repo:
                with ui.card().classes("w-full p-4 bg-gray-800/50 border border-gray-700 text-center items-center gap-3"):
                    ui.icon("source", size="2rem").classes("text-gray-500")
                    ui.label("Not a Git Repository").classes("text-sm font-semibold")
                    ui.label("Initialize local version control to track your changes over time.").classes("text-xs text-gray-400")

                    def handle_init() -> None:
                        try:
                            git_svc.init_repo()
                            ui.notify("Git repository initialized!", type="positive")
                            self.render()
                        except Exception as e:
                            ui.notify(f"Init failed: {e}", type="negative")

                    ui.button("Initialize Git", icon="add", on_click=handle_init).classes("bg-indigo-600 text-white size=sm")
                return

            # Warning if identity is missing
            if not status.has_identity:
                with ui.card().classes("w-full p-2 bg-blue-950/30 border border-blue-800/50 text-blue-200 text-[11px]"):
                    ui.label("Notice: Git author name/email not set in gitconfig. Commits might require configuration.").classes("text-xs")

            # Branch display
            with ui.row().classes("w-full items-center gap-1.5 text-xs text-gray-400"):
                ui.icon("call_split", size="0.9rem")
                ui.label(f"Branch: {status.branch_name}").classes("font-mono text-gray-300")

            # 3. Commit input section
            with ui.column().classes("w-full gap-2 p-2 bg-gray-850 rounded border border-gray-800"):
                commit_msg = ui.textarea(placeholder="Commit message...").classes("w-full text-xs").props("rows=2 dense")

                def handle_commit() -> None:
                    msg = commit_msg.value.strip()
                    if not msg:
                        ui.notify("Please enter a commit message", type="warning")
                        return
                    if not status.staged_files:
                        ui.notify("No staged changes to commit", type="warning")
                        return

                    try:
                        commit_info = git_svc.create_commit(msg)
                        commit_msg.value = ""
                        ui.notify(f"Committed {commit_info.short_sha}: {commit_info.message}", type="positive")
                        self.render()
                    except Exception as e:
                        ui.notify(f"Commit failed: {e}", type="negative")

                ui.button(
                    "Commit",
                    icon="done",
                    on_click=handle_commit,
                ).props("dense size=sm").classes("w-full bg-indigo-600 text-white")

            # 4. Staged changes section
            with ui.column().classes("w-full gap-1"):
                with ui.row().classes("w-full items-center justify-between text-xs font-semibold text-gray-400"):
                    ui.label(f"Staged Changes ({len(status.staged_files)})")
                    if status.staged_files:
                        ui.button("Unstage All", on_click=lambda: self._unstage_all(git_svc)).props("flat dense size=xs").classes("text-indigo-400")

                if not status.staged_files:
                    ui.label("No staged changes").classes("text-[11px] text-gray-500 italic pl-1")
                else:
                    for path in status.staged_files:
                        with ui.row().classes("w-full items-center justify-between px-2 py-1 bg-gray-800/40 rounded text-xs"):
                            ui.label(path).classes("font-mono text-[11px] truncate text-emerald-400")
                            ui.button(icon="remove", on_click=lambda _, p=path: self._unstage_file(git_svc, p)).props("flat round dense size=xs").classes("text-gray-400 hover:text-red-400")

            # 5. Changes (Unstaged & Untracked)
            all_changes = list(dict.fromkeys(status.unstaged_files + status.untracked_files))
            with ui.column().classes("w-full gap-1 mt-2"):
                with ui.row().classes("w-full items-center justify-between text-xs font-semibold text-gray-400"):
                    ui.label(f"Changes ({len(all_changes)})")
                    if all_changes:
                        ui.button("Stage All", on_click=lambda: self._stage_all(git_svc)).props("flat dense size=xs").classes("text-indigo-400")

                if not all_changes:
                    ui.label("Working tree clean").classes("text-[11px] text-gray-500 italic pl-1")
                else:
                    for path in all_changes:
                        is_untracked = path in status.untracked_files
                        color = "text-amber-300" if not is_untracked else "text-blue-300"

                        with ui.row().classes("w-full items-center justify-between px-2 py-1 bg-gray-800/40 rounded text-xs"):
                            ui.label(path).classes(f"font-mono text-[11px] truncate {color}")
                            with ui.row().classes("items-center gap-1"):
                                ui.button(icon="undo", on_click=lambda _, p=path: self._discard_file(git_svc, p)).props("flat round dense size=xs").classes("text-gray-400 hover:text-red-400").tooltip("Discard changes")
                                ui.button(icon="add", on_click=lambda _, p=path: self._stage_file(git_svc, p)).props("flat round dense size=xs").classes("text-gray-400 hover:text-emerald-400").tooltip("Stage file")

            # 6. Commit history log
            with ui.expansion("Recent Commits", icon="history").classes("w-full text-xs text-gray-300 border border-gray-800 rounded mt-2"):
                commits = git_svc.get_commit_log(limit=10)
                if not commits:
                    ui.label("No commits in history yet.").classes("text-[11px] text-gray-500 p-2")
                else:
                    with ui.column().classes("w-full gap-2 p-2"):
                        for c in commits:
                            with ui.column().classes("w-full border-b border-gray-800 pb-1"):
                                with ui.row().classes("items-center justify-between w-full"):
                                    ui.label(c.short_sha).classes("font-mono text-[11px] font-bold text-indigo-400")
                                    ui.label(c.date.strftime("%b %d, %H:%M")).classes("text-[10px] text-gray-500")
                                ui.label(c.message).classes("text-xs text-gray-200")

    def _stage_file(self, svc: GitService, path: str) -> None:
        try:
            svc.stage_file(path)
            self.render()
        except Exception as e:
            ui.notify(f"Stage failed: {e}", type="negative")

    def _unstage_file(self, svc: GitService, path: str) -> None:
        try:
            svc.unstage_file(path)
            self.render()
        except Exception as e:
            ui.notify(f"Unstage failed: {e}", type="negative")

    def _stage_all(self, svc: GitService) -> None:
        try:
            svc.stage_all()
            self.render()
        except Exception as e:
            ui.notify(f"Stage all failed: {e}", type="negative")

    def _unstage_all(self, svc: GitService) -> None:
        try:
            svc.unstage_all()
            self.render()
        except Exception as e:
            ui.notify(f"Unstage all failed: {e}", type="negative")

    def _discard_file(self, svc: GitService, path: str) -> None:
        try:
            svc.discard_changes(path)
            # If current active chapter is this file, reload it
            if self.state.active_chapter and self.state.active_chapter.path.name == path:
                self.state.set_active_chapter(self.state.active_chapter)
            ui.notify(f"Discarded changes on '{path}'", type="info")
            self.render()
        except Exception as e:
            ui.notify(f"Discard failed: {e}", type="negative")
