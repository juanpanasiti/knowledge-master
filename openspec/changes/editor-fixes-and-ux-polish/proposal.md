## Why

During hands-on editing workflows, several critical data integrity and UX defects were identified in the active workspace and Vditor Markdown integration:
1. The editor autosave was silently wiping chapter contents to 0 bytes and locking the word count at 0 words due to an event payload parsing mismatch.
2. Opening existing ebooks with `"description": null` caused fatal Pydantic `ValidationError` crashes.
3. Ordered lists lacked numbers due to CSS preflight resets.
4. Tables in dark mode rendered as glaring white boxes with unreadable white-on-white text.
5. Nested lists trapped users inside indented list items with no ability to break out to a normal root-level paragraph.
6. Toolbar icons and several dashboard/sidebar actions lacked visible tooltips.

Resolving these issues in a unified change ensures complete data safety, visual consistency, and a refined editing experience.

## What Changes

- **Fix Autosave and Word Count Tracking**: Correct the `CustomEvent` payload handling in the NiceGUI-to-Python bridge (`event.args['detail']['content']`) to ensure typed text is saved to disk and word count updates dynamically.
- **Robust Ebook Metadata Resilience**: Support `description: str | None = ""` in `EbookMetadata` so that opening projects with null descriptions never crashes the application.
- **Ordered List Number Display**: Reinstate `list-style-type: decimal !important` for ordered lists (`ol`) to override CSS preflight resets.
- **Dark Mode Table Styling**: Provide curated dark theme styles for tables (`table`, `th`, `tr`, `td`), replacing hardcoded light backgrounds with dark slate backgrounds, high-contrast text, and subtle borders.
- **List Outdent and Document Escape Ergonomics**: Add `outdent` and `indent` toolbar buttons to Vditor, and implement keyboard handling (Enter on empty item, Backspace at start, Shift+Tab) allowing users to unindent nested lists all the way back to root paragraph mode.
- **Comprehensive Tooltip Coverage**: Adjust Vditor toolbar tooltips to render downwards (`tipPosition: 's'`) preventing overflow clipping, and attach tooltips to all interactive icon buttons in NiceGUI (`more_vert`, `remove`, `close`, `insert_image`).

## User Impact

- **Goals**:
  - Guarantee that chapter edits are reliably persisted to disk without data loss.
  - Ensure the word count accurately reflects chapter content immediately after autosaving.
  - Prevent application crashes when loading ebooks created with null metadata fields.
  - Provide an aesthetically pleasing, fully legible dark mode presentation for tables and numbered lists.
  - Enable fluid list editing, indenting, and escaping back to normal document paragraphs.
  - Ensure every interactive icon across the application provides an informative tooltip on hover.
- **Non-Goals**:
  - Rewriting the underlying Markdown parser (Lute) or replacing Vditor.
  - Adding multi-level undo history management beyond Vditor's native history stack.
  - Implementing WYSIWYG table editing popups or complex cell merging.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `markdown-editor`: Update requirements for debounced autosave persistence, list rendering (ordered list decimals and list escaping/outdent), dark mode table contrast, and toolbar tooltip visibility.
- `ebook-workspace`: Update requirements for metadata parsing resilience against null fields and tooltip availability across workspace and dashboard action buttons.

## Impact

- **Affected Code**:
  - `src/ebook_editor/ui/components/editor.py`: Event handling, toolbar configuration, and CSS injection.
  - `src/ebook_editor/core/models.py`: `EbookMetadata` validation for null description fields.
  - `src/ebook_editor/ui/workspace_view.py`: Save handling, word count updates, and header tooltips.
  - `src/ebook_editor/ui/components/file_tree.py`: Action button tooltips.
  - `src/ebook_editor/ui/components/git_panel.py`: Staging action tooltips.
  - `src/ebook_editor/ui/dashboard.py`: Recent project close button tooltips.
- **SemVer Impact**: Patch (`0.1.0` -> `0.1.1`) as this change fixes critical bugs and refines existing features without breaking public APIs.
