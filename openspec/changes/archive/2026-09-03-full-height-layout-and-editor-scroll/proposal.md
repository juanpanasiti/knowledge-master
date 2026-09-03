## Why

Currently, the NiceGUI application shell collapses vertically to fit its contents because intermediate Quasar and page container elements default to automatic height. This causes an empty, dead space at the bottom of the window in both the dashboard and editor views. Furthermore, project lists in the dashboard and the editor writing sheet do not have independent vertical scrolling, and switching chapters in the file tree can crash with a slot deletion RuntimeError.

Fixing the layout hierarchy ensures the application feels like a true full-window native desktop app where containers occupy 100% of available viewport space, content lists scroll cleanly within their boundaries, the editor sheet handles its own vertical scrolling, and users can toggle between centered and full-width writing modes.

## What Changes

- **Full-Viewport CSS Hierarchy**: Enforce `height: 100% !important`, `min-height: 0 !important`, and proper flex column rules across `#app`, `.q-layout`, `.q-page-container`, `.q-page`, and `.nicegui-content`.
- **Editor Sheet Vertical Scroll**: Configure Vditor containers so the editor toolbar remains fixed at the top while the writing sheet (`pre.vditor-reset`) expands to the bottom border and handles vertical scrolling independently.
- **Editor Reading Width Toggle**: Add a toggle button in the editor subheader allowing users to switch between a centered readable width (`max-w-4xl mx-auto`) and full width (`w-full`).
- **Flowing Dashboard Project Lists**: Update the dashboard view so the columns and project card lists (`Recent Projects` and `Workspace Library`) expand vertically to the bottom of the window with smooth padding and dedicated vertical scrolling (`overflow-y-auto`).
- **Resilient Chapter Selection**: Fix chapter selection in the sidebar file tree to prevent `RuntimeError: The parent element this slot belongs to has been deleted` by avoiding destructive re-renders during active event processing and invoking editor JavaScript through the element's client instance.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `markdown-editor`: Adds requirements for full-height editor layout with sheet vertical scrolling, readable width toggle (full vs centered), and crash-resilient chapter switching.
- `ebook-workspace`: Adds requirements for full-height dashboard layout and independently scrollable project lists.

## Impact

- **Affected UI Components**:
  - `src/ebook_editor/main.py`: Global layout CSS styles.
  - `src/ebook_editor/ui/dashboard.py`: Dashboard container, columns, and scrollable project lists.
  - `src/ebook_editor/ui/workspace_view.py`: Main split container, subheader controls, width state.
  - `src/ebook_editor/ui/components/editor.py`: Vditor CSS rules, width toggle wrapper, JavaScript execution safety.
  - `src/ebook_editor/ui/components/file_tree.py`: Selection handler and active state update logic without slot deletion.
- **Dependencies**: No new external dependencies required.
- **Breaking Changes**: None.
