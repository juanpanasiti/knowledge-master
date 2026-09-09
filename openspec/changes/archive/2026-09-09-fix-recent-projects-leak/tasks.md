## 1. Test Environment Isolation

- [x] 1.1 Create `tests/conftest.py` with an autouse pytest fixture that redirects `ebook_editor.core.config.DEFAULT_APP_DIR` to a temporary directory, and verify with `uv run pytest`.
- [x] 1.2 Update `tests/test_ui_layout.py` lines where `AppState()` is instantiated to pass an isolated `ConfigManager(root_dir=tmp_path)`, and verify tests pass.

## 2. Recent Workspace Validation & Sanitization

- [x] 2.1 Update `_render_recent_shelf` in `src/ebook_editor/ui/dashboard.py` to verify `ws.is_valid()` before rendering cards, ignoring invalid or missing ebook directories.
- [x] 2.2 Add a helper method in `src/ebook_editor/core/config.py` or `src/ebook_editor/core/models.py` to prune non-existent and invalid paths from `recent_ebooks`.
- [x] 2.3 Clean up existing phantom `/tmp/pytest-...` paths from the user's `~/knowledge-master/config.json`.

## 3. Testing & Verification

- [x] 3.1 Add unit tests in `tests/test_dashboard.py` and `tests/test_config.py` verifying that invalid or missing recent paths are not rendered and are properly pruned.
- [x] 3.2 Run the full test suite with `uv run pytest` and confirm zero entries are leaked into `~/knowledge-master/config.json`.

## 4. Versioning & Final Validation

- [x] 4.1 Bump patch version in `pyproject.toml` and review documentation.
- [x] 4.2 Perform final validation verifying all requirements in `proposal.md` and `specs/ebook-workspace/spec.md` are satisfied.
