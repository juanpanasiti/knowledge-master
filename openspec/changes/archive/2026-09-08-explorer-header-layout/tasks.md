# Tasks: Explorer Header Layout and Lifecycle Fixes

## 1. Explorer Header Slot Refactor

- [x] 1.1 Refactor `_render_content_section` in `FileTreeComponent` (`src/ebook_editor/ui/components/file_tree.py`) to render the section header row within `exp.add_slot("header")` with `flex-1 items-center justify-between pr-2`, and verify that the Content icon, title, badge, and `+` button remain visible when the section is collapsed.
- [x] 1.2 Refactor `_render_resources_section` in `FileTreeComponent` (`src/ebook_editor/ui/components/file_tree.py`) to render the section header row within `exp.add_slot("header")` with `flex-1 items-center justify-between pr-2`, and verify that the Resources icon, title, badge, and `+` button remain visible when the section is collapsed.
- [x] 1.3 Refactor `_render_assets_section` in `FileTreeComponent` (`src/ebook_editor/ui/components/file_tree.py`) to render the section header row within `exp.add_slot("header")` with `flex-1 items-center justify-between pr-2`, and verify that the Assets icon, title, badge, and upload button remain visible when the section is collapsed.
- [x] 1.4 Refactor `_render_dist_section` in `FileTreeComponent` (`src/ebook_editor/ui/components/file_tree.py`) to render the section header row within `exp.add_slot("header")` with `flex-1 items-center justify-between pr-2`, and verify that the Dist icon, title, and badge remain visible when the section is collapsed.

## 2. Event Propagation and Lifecycle Fixes

- [x] 2.1 Attach `js_handler='(e) => { e.stopPropagation(); emit(); }'` to the header action buttons (`+` in Content and Resources, `file_upload` in Assets), and verify that clicking each button triggers its dialog without collapsing or expanding the parent accordion section.
- [x] 2.2 Reorder `ui.notify()` before `self.render()` in `_show_new_file_dialog` and `_show_rename_dialog` within `src/ebook_editor/ui/components/file_tree.py`, and verify that creating a chapter or resource file completes and displays the toast notification without raising `RuntimeError: The parent element this slot belongs to has been deleted.`

## 3. Versioning, Documentation, and Validation

- [x] 3.1 Bump version from `0.4.0` to `0.4.1` in `pyproject.toml`, and verify with `uv run python -c "import ebook_editor; print('ready')"` that packaging configurations are valid.
- [x] 3.2 Review `README.md` to ensure documentation matches the current component layout and update if needed.
- [x] 3.3 Run automated tests with `uv run pytest` and perform manual verification of the accordion explorer to validate that all proposal goals and spec scenarios are satisfied.
