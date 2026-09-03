## 1. Full-Height Global CSS and Layout Infrastructure

- [x] 1.1 Update `GLOBAL_STYLES` in `src/ebook_editor/main.py` to enforce 100% height and flex column inheritance across `html`, `body`, `#app`, `.q-layout`, `.q-page-container`, `.q-page`, and `.nicegui-content`, and verify layout expansion without bottom blank bars.
- [x] 1.2 Verify `root_container` in `src/ebook_editor/main.py` properly expands to 100% of the viewport and children stretch to full height.

## 2. Flowing Dashboard View and Scrollable Lists

- [x] 2.1 Refactor `DashboardView` container and column layout in `src/ebook_editor/ui/dashboard.py` to use flex column stretching with a fixed header.
- [x] 2.2 Configure `Recent Projects` and `Workspace Library` project card lists with `flex-1 min-h-0 overflow-y-auto` and bottom padding, and verify both lists scroll cleanly when populated with multiple projects.

## 3. Editor Sheet Scrolling and Reading Width Toggle

- [x] 3.1 Update Vditor container and CSS rules in `src/ebook_editor/ui/components/editor.py` so the writing sheet (`pre.vditor-reset`) spans to the bottom window border with dedicated vertical scrolling while the toolbar stays pinned.
- [x] 3.2 Add a width mode state and an interactive toggle button in the editor subheader in `src/ebook_editor/ui/workspace_view.py` to alternate between centered readable mode (`max-w-4xl mx-auto`) and full-width mode (`w-full`), verifying the width switches dynamically.

## 4. Chapter Selection Stability & Error Prevention

- [x] 4.1 Update `VditorEditor.set_content` in `src/ebook_editor/ui/components/editor.py` to safely execute JavaScript via the element's client instance.
- [x] 4.2 Update chapter selection in `src/ebook_editor/ui/components/file_tree.py` so active state styling updates without destroying slots during active click event handling, verifying chapter switching produces no runtime errors.

## 5. Verification and Integration Testing

- [x] 5.1 Run test suite (`pytest`) to ensure no regressions in workspace or editor core functions.
- [x] 5.2 Verify complete UI flow in the running app (dashboard full height, project list scrolling, editor full height, writing sheet scrolling, and width toggle).
