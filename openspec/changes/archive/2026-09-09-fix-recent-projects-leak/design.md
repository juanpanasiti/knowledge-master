## Context

See `proposal.md` for motivation. Currently:
- `ConfigManager` in `src/ebook_editor/core/config.py` defaults to `DEFAULT_APP_DIR = Path.home() / "knowledge-master"`.
- `AppState` initializes a default `ConfigManager()` if none is supplied.
- When `AppState.set_active_workspace(ws)` is called, it registers `ws.root` in `recent_ebooks`.
- Tests in `tests/test_ui_layout.py` instantiate `AppState()` directly without supplying a mock or isolated `ConfigManager`.
- Running `pytest` creates temporary directories in `/tmp/pytest-of-<user>/.../book` and records them into the user's real `~/knowledge-master/config.json`.
- `dashboard._render_recent_shelf` checks only `if not p.exists(): continue`, falling back to `title = p.name` when `not ws.is_valid()`. As a result, temporary test directories that still exist in `/tmp` are displayed as phantom "book" cards without metadata or covers.

## Goals / Non-Goals

**Goals:**
- **Strict Test Isolation**: Guarantee that tests never touch or mutate the user's real `~/knowledge-master/config.json` by adding a global pytest fixture in `tests/conftest.py` and isolating individual tests.
- **Strict Recent Shelf Validation**: Ensure `_render_recent_shelf` in `dashboard.py` only displays workspaces that pass `ws.is_valid()`, ignoring non-ebook directories.
- **Recent List Sanitization**: Provide an automatic or on-load cleanup mechanism in `ConfigManager` / `AppSettings` to prune non-existent and invalid directories from `recent_ebooks`.

**Non-Goals:**
- Altering the visual design or animations of the Recent Projects shelf.
- Modifying how `metadata.json` is generated or validated.

## Decisions

### 1. Global Test Isolation in `tests/conftest.py`
- **Choice**: Create `tests/conftest.py` with an autouse fixture that patches `ebook_editor.core.config.DEFAULT_APP_DIR` to a temporary directory for every test session or function.
- **Rationale**: While we also update `test_ui_layout.py` to pass an isolated `ConfigManager`, a global fixture ensures that any future tests or components instantiating `AppState()` or `ConfigManager()` will never touch the user's home directory.
- **Alternatives Considered**: Only updating `test_ui_layout.py`. Rejected because future tests could easily reintroduce the leak.

### 2. Validate Workspaces in `_render_recent_shelf`
- **Choice**: In `dashboard._render_recent_shelf`, check `if not ws.is_valid(): continue` instead of only `if not p.exists(): continue`.
- **Rationale**: A directory without `metadata.json` is not a valid ebook project. Displaying it as a fallback card confuses users and pollutes the workspace.
- **Alternatives Considered**: Displaying a broken card with an error icon. Rejected because phantom or invalid directories should not appear in the shelf.

### 3. Prune Invalid Recent Entries in `ConfigManager`
- **Choice**: Add `prune_invalid_recents()` (or clean up inside `load_settings()` / `_render_recent_shelf`) to remove paths from `recent_ebooks` that either no longer exist or fail `is_valid()`.
- **Rationale**: Keeps `config.json` clean and prevents dead paths from accumulating over time.

## Risks / Trade-offs

- **[Risk]** If an ebook lives on a temporarily unmounted drive, aggressive pruning on app startup might delete it from recent history.
  → **Mitigation**: Filter invalid entries at render time so they don't show up in the UI, and only prune paths that definitively do not exist on disk (or provide explicit pruning).
