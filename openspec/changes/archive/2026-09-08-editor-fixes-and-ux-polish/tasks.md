## 1. Core Models and Metadata Resilience

- [x] 1.1 Update `EbookMetadata` in `src/ebook_editor/core/models.py` to allow `description: str | None = ""` with a field validator converting `None` to `""`, and verify with a unit test loading a JSON payload with `"description": null`.
- [x] 1.2 Add unit tests in `tests/test_models.py` verifying that metadata serialization and deserialization seamlessly handle null, missing, and populated description fields.

## 2. Editor Component Event Handling and Styling Fixes

- [x] 2.1 Update `_handle_autosave` in `src/ebook_editor/ui/components/editor.py` to robustly unpack `content` from `event.args.get("detail", {}).get("content")` with fallback to `event.args.get("content", "")`, preventing empty saves.
- [x] 2.2 Update `VDITOR_HEAD_HTML` in `src/ebook_editor/ui/components/editor.py` to include `.vditor-reset ol { list-style-type: decimal !important; padding-left: 1.75rem !important; }` (including nested alpha/roman counters), and verify ordered list numbers are restored.
- [x] 2.3 Add comprehensive dark mode styling for `.vditor-reset table`, `th`, `tr`, `td`, and row hover states in `VDITOR_HEAD_HTML` inside `src/ebook_editor/ui/components/editor.py` to eliminate blinding white backgrounds and restore high contrast.
- [x] 2.4 Add `'outdent'` and `'indent'` to the Vditor toolbar items array in `src/ebook_editor/ui/components/editor.py`, configure items with `tipPosition: 's'`, and adjust toolbar tooltip CSS so tooltips float downwards without being clipped by `overflow: hidden`.
- [x] 2.5 Implement a keydown listener in `initKmEditor` in `src/ebook_editor/ui/components/editor.py` for Vditor IR mode: when on an empty list item or paragraph within a list, pressing Enter or Backspace at offset 0 executes an outdent to escape nested lists back to root level.

## 3. Workspace UI Tooltips and Polish

- [x] 3.1 Add descriptive tooltips to icon buttons in `src/ebook_editor/ui/workspace_view.py` (`_show_insert_image_dialog` button).
- [x] 3.2 Add tooltips to chapter options button (`more_vert`) in `src/ebook_editor/ui/components/file_tree.py`.
- [x] 3.3 Add tooltips to unstage file button (`remove`) in `src/ebook_editor/ui/components/git_panel.py`.
- [x] 3.4 Add tooltips to remove recent project button (`close`) in `src/ebook_editor/ui/dashboard.py`.

## 4. Testing, Versioning, and Documentation

- [x] 4.1 Bump project version in `pyproject.toml` from `0.1.0` to `0.1.1` (patch release for bug fixes and UX enhancements).
- [x] 4.2 Review and update `README.md` if any editor controls or keyboard navigation details need updating.
- [x] 4.3 Run full test suite with `uv run pytest` to ensure all existing and new unit tests pass cleanly.
- [x] 4.4 Perform end-to-end verification of the editor workflow: verify that typing text saves to disk, word count updates, ordered list numbers are visible, tables display with dark theme, nested lists escape to normal paragraphs, and tooltips display across all icons.
