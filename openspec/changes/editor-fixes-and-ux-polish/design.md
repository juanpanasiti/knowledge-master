## Context

The application pairs a Python/NiceGUI frontend with Vditor in Instant Rendering (IR) mode. While the editor core and workspace models are established, edge cases in event serialization, model validation, and styling have introduced friction:
- NiceGUI's event dispatcher serializes DOM `CustomEvent` objects into a dictionary where client parameters are encapsulated under the `detail` property (`event.args = {'detail': {'content': ...}, ...}`).
- Pydantic models with non-optional string defaults (`description: str = ""`) reject explicit JSON `null` values (`{"description": null}`).
- NiceGUI / Quasar base CSS injects a global reset (`ol, ul { list-style: none }`) which overrides browser defaults for `<ol>` because Vditor only explicitly restyles `<ul>`.
- Vditor's default CSS for tables provides hardcoded light colors (`#fff`, `#fafbfc`), causing severe contrast degradation in dark theme.
- Vditor's IR DOM structure nests paragraphs within list items during multi-level indentations, preventing intuitive outdenting when users attempt to return to the root level.
- Vditor toolbar items default to north tooltips (`__n`), which get clipped by the top container's `overflow: hidden` rule.

## Goals / Non-Goals

**Goals:**
- Implement resilient event unpacking in `_handle_autosave` that safely inspects `detail.content` or falls back to root `content`.
- Make `EbookMetadata.description` resilient to `None`/`null` inputs by normalizing to an empty string.
- Provide definitive CSS overrides in `editor.py` for ordered list numbering and dark-mode table styling.
- Integrate `outdent` and `indent` actions into the Vditor toolbar and attach an IR keyboard event handler to gracefully exit nested lists to the root margin.
- Re-orient Vditor tooltips to south (`tipPosition: 's'`) with downward floating CSS, and add missing tooltips across NiceGUI buttons.

**Non-Goals:**
- Custom table cell resizing or WYSIWYG table context menus.
- Migrating away from Vditor or modifying upstream vendored minified scripts directly. All fixes must be injected cleanly via Python wrappers and CSS.

## Decisions

### 1. Robust Event Payload Unpacking in `VditorEditor`
- **Decision**: In `_handle_autosave(self, event)`, inspect whether `event.args` is a dictionary with a `"detail"` mapping. If present, extract `content` from `detail["content"]`; otherwise fall back to `event.args.get("content", "")`.
- **Rationale**: Keeps the Python handler backward-compatible with direct event arguments while correctly handling browser-dispatched `CustomEvent` payloads.
- **Alternatives Considered**: Using NiceGUI's `args=['detail.content']` in `element.on()`. While viable, extracting dynamically in Python handles varying NiceGUI event structures without risking client-side serialization errors.

```
Client (Vditor input event)
  │ (debounced 500ms)
  ▼
CustomEvent('editor-autosave', { detail: { content: val } })
  │ (Socket.io event)
  ▼
Python NiceGUI Client (event.args = {'detail': {'content': '...'}, ...})
  │
  ▼
VditorEditor._handle_autosave()
  │ detail.get('content')
  ▼
WorkspaceView._handle_editor_save()
  ├── ChapterFile.write_content(content)
  ├── _update_word_count(content)
  └── _save_status_label.set_text("Saved")
```

### 2. Pydantic Model Normalization for Optional Metadata Fields
- **Decision**: Define `description: str | None = ""` in `EbookMetadata` and add a `@field_validator('description', mode='before')` that converts `None` to `""`.
- **Rationale**: Ensures external or manually edited `metadata.json` files containing `"description": null` load seamlessly without breaking runtime model validation.

### 3. CSS Injection for Ordered Lists and Dark Tables
- **Decision**: Inject targeted CSS rules into `VDITOR_HEAD_HTML`:
  - Ordered lists: `.vditor-reset ol { list-style-type: decimal !important; padding-left: 1.75rem !important; }` (with nested alpha/roman rules).
  - Tables: Override `.vditor-reset table`, `.vditor-reset table tr`, and `.vditor-reset table th` with dark theme slate colors (`#1a202c`, `#242c3d`), subtle borders (`rgba(255,255,255,0.1)`), and readable text (`#d1d5db` / `#f3f4f6`).
- **Rationale**: Overriding through `VDITOR_HEAD_HTML` isolates styling to the component level without modifying upstream static assets, ensuring zero build pipeline regressions.

### 4. Nested List Escape and Outdent Ergonomics
- **Decision**:
  - Add `'outdent'` and `'indent'` to the Vditor toolbar configuration array.
  - In `initKmEditor`, attach a `keydown` handler on the Vditor IR content container: when the cursor is in an empty paragraph or list item within a list (`LI`), pressing `Enter` or `Backspace` at offset 0 triggers an outdent operation (`ct` or programmatic click on the outdent toolbar button), eventually escaping to the root level.
- **Rationale**: Aligns the editor with familiar Markdown and word-processing ergonomics (e.g., Obsidian, Notion).

### 5. South-Oriented Tooltips and Global Tooltip Coverage
- **Decision**:
  - Configure Vditor toolbar items with `tipPosition: 's'` and enforce downward positioning in CSS (`.vditor-toolbar .vditor-tooltipped::after { top: 100% !important; bottom: auto !important; }`).
  - Add `.tooltip(...)` calls to icon buttons in `file_tree.py` (`more_vert`), `git_panel.py` (`remove`), `dashboard.py` (`close`), and `workspace_view.py` (`insert_image`).
- **Rationale**: Solves the clipping issue completely because elements positioned below the top toolbar render within the visible document canvas.

## Risks / Trade-offs

- **[Risk]** Keyboard event handler in IR mode interferes with normal Enter / Backspace typing in regular paragraphs.
  - **Mitigation**: Guard the event listener strictly: check `e.key === 'Enter' || e.key === 'Backspace'`, check that the active selection container is within an `LI` or nested list `<p>`, and check that text content is empty or caret offset is 0.
- **[Risk]** Theme switching doesn't update table styles if a user switches to light mode.
  - **Mitigation**: Scope dark table styles to `.vditor--dark` or the dark sheet wrapper (`.editor-sheet-centered`, `.editor-sheet-full`) to preserve light mode default appearance if light mode is selected.
