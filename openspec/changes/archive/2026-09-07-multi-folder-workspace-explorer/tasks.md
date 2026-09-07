# Tasks: Multi-Folder Workspace Explorer and Resources Management

## 1. Core Workspace and Configuration

- [x] 1.1 Generalize `ChapterFile` into `WorkspaceFile` in `src/ebook_editor/core/workspace.py` while maintaining `ChapterFile = WorkspaceFile` for backwards compatibility, and verify existing chapter tests pass with `uv run pytest tests/test_workspace.py`.
- [x] 1.2 Update `EbookWorkspace` in `src/ebook_editor/core/workspace.py` to ensure `resources/` directory exists, implement `list_content_files()`, `list_resource_files()`, `list_asset_files()`, `list_dist_files()`, and resource CRUD (`create_resource`, `rename_resource`, `delete_resource`), and verify with new unit tests in `tests/test_workspace.py`.
- [x] 1.3 Update `src/ebook_editor/core/config.py` and `AppSettings` to persist and retrieve per-workspace accordion expansion states in `config.json`, and verify with unit tests in `tests/test_config.py`.
- [x] 1.4 Update `src/ebook_editor/core/asset_server.py` to add `/api/workspace/dist/{file_path:path}` endpoint with strict path traversal validation against `dist_dir`, and verify with endpoint tests for PDF/EPUB serving and traversal security.

## 2. UI State and Explorer Component

- [x] 2.1 Update `src/ebook_editor/ui/state.py` to track `active_file: WorkspaceFile | None`, maintaining backwards compatibility with `active_chapter` listeners, and verify state file switching behavior.
- [x] 2.2 Refactor `src/ebook_editor/ui/components/file_tree.py` into a multi-folder accordion explorer with four collapsible sections (`Content`, `Resources`, `Assets`, and `Dist`) using `ui.expansion`.
- [x] 2.3 Connect accordion expansion state changes to `ConfigManager` to persist and restore open/closed sections across workspace sessions.
- [x] 2.4 Implement image asset preview dialog in `file_tree.py` with image viewing and 1-click "Copy Markdown Link" (`![alt](assets/filename)`) clipboard functionality.
- [x] 2.5 Implement Dist build interaction in `file_tree.py` enabling browser tab viewing for `.pdf` files and download handling for `.epub` files.

## 3. Integration, Verification, and Versioning

- [x] 3.1 Wire the new explorer into `src/ebook_editor/ui/workspace_view.py` and verify switching between `content/` markdown files and `resources/` files in Vditor without editor regressions.
- [x] 3.2 Update `pyproject.toml` with a minor version bump and update `README.md` to document the `resources/` directory and new explorer capabilities.
- [x] 3.3 Run full automated test suite with `uv run pytest` and verify all existing and new unit/integration tests pass.
- [x] 3.4 Perform final end-to-end validation confirming that all functional and UI requirements defined in `proposal.md` and delta specs are satisfied.
