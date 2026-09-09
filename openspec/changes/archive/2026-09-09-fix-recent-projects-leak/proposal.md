## Why

Running unit tests (such as `test_ui_layout.py`) accidentally contaminated the user's real `~/knowledge-master/config.json` with temporary pytest directories named `book`. Furthermore, the dashboard's Recent Projects shelf does not verify whether recent paths point to valid ebook workspaces (with `metadata.json`), causing non-existent or temporary folders to display as generic "book" cards without covers or authors.

## What Changes

- **Test Suite Isolation**: Introduce a global pytest fixture or mock in `conftest.py` ensuring that `DEFAULT_APP_DIR` / `ConfigManager` uses a temporary directory during tests, preventing test runs from writing to the user's production `~/knowledge-master/` environment. Also fix direct `AppState()` instantiations in `test_ui_layout.py` to use isolated config managers.
- **Recent Projects Validation & Pruning**: Enhance `dashboard._render_recent_shelf` and `ConfigManager` to verify `EbookWorkspace.is_valid()` before rendering recent cards. Filter out invalid workspaces that lack `metadata.json` or no longer exist.
- **Config Sanitization**: Automatically purge or filter non-existent and invalid ebook paths from `recent_ebooks` in `AppSettings` / `ConfigManager`.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `ebook-workspace`: Add requirement that the Recent Projects shelf validates workspaces with `is_valid()` before rendering, and that invalid or missing paths are pruned rather than displayed as broken generic cards.

## Impact

- **Affected Code**:
  - `src/ebook_editor/ui/dashboard.py`: filter out invalid workspaces in `_render_recent_shelf`.
  - `src/ebook_editor/core/config.py` & `src/ebook_editor/core/models.py`: support sanitization/pruning of invalid recent entries.
  - `tests/conftest.py`: add autouse fixture to isolate `DEFAULT_APP_DIR` / configuration for all tests.
  - `tests/test_ui_layout.py`: pass isolated `ConfigManager` to `AppState`.
- **User Experience**: The phantom "book" cards from previous test runs will vanish from Recent Projects, and only genuine, valid ebooks will be displayed.
- **Dependencies & APIs**: No external dependencies added; no breaking API changes.
