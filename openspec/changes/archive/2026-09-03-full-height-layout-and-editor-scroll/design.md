## Context

The application runs NiceGUI with Quasar components and a native webview window. The default DOM layout created by NiceGUI wraps all views inside `#app > .q-layout > .q-page-container > main.q-page.nicegui-content`. In standard Quasar layouts, `.q-page-container` has `height: auto`, which causes percentage-based child dimensions (`h-full` / `height: 100%`) to compute to content height rather than stretching to the full window.

In addition, Vditor's Instant Rendering mode houses a `pre.vditor-reset` element that serves as the editable sheet. Without a complete flex height chain, this sheet collapses to the height of adjacent sidebar elements, leaving a large dead space at the bottom of the window. When users switch chapters, the sidebar currently triggers a full re-render within the active click event, causing NiceGUI slot deletion errors during subsequent JavaScript calls.

See [proposal.md](file:///home/juan/Projects/knowledge-master/openspec/changes/full-height-layout-and-editor-scroll/proposal.md) for background and motivation.

## Goals / Non-Goals

**Goals:**
- Provide a full-window layout where containers stretch seamlessly from top to bottom without any dead space at the base.
- Ensure the editor's markdown sheet spans to the bottom window border and scrolls vertically, with toolbars and headers remaining pinned.
- Implement an interactive reading width toggle in the editor subheader to switch between centered readable mode (`max-w-4xl mx-auto`) and full-width mode (`w-full`).
- Enable the dashboard project lists to flow cleanly toward the bottom of the window with dedicated vertical scrolling per column.
- Prevent `RuntimeError: The parent element this slot belongs to has been deleted` during chapter selection.

**Non-Goals:**
- Altering the backend ebook metadata or file storage schema.
- Replacing Vditor with a different editor library.
- Introducing multi-window or tabbed document editing.

## Decisions

### Decision 1: Full-Viewport CSS Inheritance Chain
- **Approach**: Extend `GLOBAL_STYLES` in `src/ebook_editor/main.py` with explicit rules targeting `#app`, `.q-layout`, `.q-page-container`, `.q-page`, and `.nicegui-content`:
  ```css
  html, body, #app, .q-layout, .q-page-container, .q-page, .nicegui-content {
    height: 100% !important;
    max-height: 100% !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
  }
  ```
- **Rationale**: CSS percentage heights require every ancestor node up to `<html>` to have an explicit height or flex stretching. Applying this rule uniformly ensures intermediate Quasar container elements never collapse to content size.
- **Alternatives Considered**: Using `100vh` on individual child containers was rejected because viewport units do not account for native window titlebars or padding properly, leading to double scrollbars.

### Decision 2: Writing Width Toggle Mode in Workspace View
- **Approach**: In `WorkspaceView`, introduce an editor width state (defaulting to centered `max-w-4xl mx-auto`) with a toggle button in the editor subheader. Clicking the button toggles between:
  - Centered mode: `w-full max-w-4xl mx-auto` for ergonomic, focused reading and writing.
  - Full width mode: `w-full max-w-none` utilizing the complete horizontal space of the center column.
- **Rationale**: Writing long-form text across ultra-wide monitors strains reading readability, while editing wide tables or code blocks benefits from full width. Providing an on-the-fly toggle gives users immediate control.

### Decision 3: Flowing Dashboard Columns with Pinned Header
- **Approach**: Restructure `DashboardView.container` to be a flex column taking 100% height (`w-full h-full flex-1 min-h-0 flex flex-col p-8 max-w-6xl mx-auto`).
  - Top header is fixed (`flex-shrink-0`).
  - The content row takes the remaining height (`w-full flex-1 min-h-0 mt-6 gap-8`).
  - Each column (`Recent Projects` and `Workspace Library`) has a column header (`flex-shrink-0`) and a scrollable list container (`w-full flex-1 min-h-0 overflow-y-auto pr-2 gap-2`).
- **Rationale**: Ensures the dashboard stays within the window boundary even if there are dozens of projects, with clean, independent scrolling.

### Decision 4: Stable Chapter Selection Execution
- **Approach**: In `src/ebook_editor/ui/components/file_tree.py` and `src/ebook_editor/ui/components/editor.py`:
  - In `VditorEditor.set_content()`, execute JavaScript safely via `self.element.run_javascript()` or `self.element.client.run_javascript()` instead of bare global `ui.run_javascript()`.
  - When selecting a chapter, update the selected state without destructively tearing down the active slot element before the event completes.
- **Rationale**: Eliminates the slot parent deletion exception when switching between chapters.

## Risks / Trade-offs

- **[Risk] Vditor width toggle might cause layout jumps in rendered markdown tables or code** → **Mitigation**: Use smooth CSS transitions or let Vditor's internal width listeners adapt naturally without reinitializing the instance.
- **[Risk] Native desktop window resizing might clip dashboard padding** → **Mitigation**: Use standard padding (`p-6` or `p-8`) with `box-sizing: border-box` and minimum width/height constraints on window startup.
