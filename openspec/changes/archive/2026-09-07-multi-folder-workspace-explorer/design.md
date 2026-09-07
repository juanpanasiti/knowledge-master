# Design: Multi-Folder Workspace Explorer and Resources Management

## Context

The current sidebar (`FileTreeComponent`) lists only markdown files from `content/` and titles them "Chapters". The application has no visual representation for media in `assets/`, generated files in `dist/`, or supplementary materials. Furthermore, authors working on technical documentation or books need a dedicated location for source diagrams (e.g. Mermaid `.mmd` files), research notes, and outlines without risking accidental inclusion in the published EPUB or PDF output.

See `proposal.md` for motivation and `specs/` for behavioral requirements.

## Goals / Non-Goals

**Goals:**
- Restructure the sidebar into four collapsible accordion sections: `Content`, `Resources`, `Assets`, and `Dist`.
- Persist the expanded/collapsed state of each accordion section per workspace across application reloads.
- Establish `resources/` as a first-class project directory in `EbookWorkspace` for authoring materials, excluded from export compilation.
- Allow opening and editing `.md`, `.mmd`, and `.txt` files from `resources/` in the Vditor editor with full autosave support.
- Provide a clean modal preview for images in `assets/` with an instant "Copy Markdown Link" clipboard action.
- Enable direct viewing of generated PDF builds in a browser tab and downloading/launching of EPUB builds from `dist/`.

**Non-Goals:**
- In-app interactive EPUB reading simulator (deferred to a dedicated future change for full fidelity e-reader emulation).
- Multi-level nested folder creation inside `content/` or `resources/` (flat natural-sorted lists remain standard).
- Automatic compilation of Mermaid `.mmd` into PNG on save (diagram rendering is previewed in Vditor; final PNGs are placed in `assets/`).

## Decisions

### 1. File Abstraction and Backward Compatibility
- **Choice**: Generalize `ChapterFile` into a unified `WorkspaceFile` dataclass (representing any editable text/markdown file in `content/` or `resources/`), while retaining `ChapterFile = WorkspaceFile` and `list_chapters()` as aliases.
- **Rationale**: Prevents breaking existing tests and references while allowing `AppState` and `VditorEditor` to seamlessly handle files from both `content/` and `resources/`.
- **Alternatives Considered**: Creating completely separate `ResourceFile` and `ChapterFile` classes with duplicate read/write logic. Rejected due to unnecessary boilerplate.

### 2. Accordion Component Architecture
- **Choice**: Use Quasar's `q-expansion-item` via NiceGUI's `ui.expansion()` for the 4 sections (`Content`, `Resources`, `Assets`, `Dist`).
- **Rationale**: Provides native collapsible header animations, badges for file counts, clean action buttons in headers (e.g., `+` for adding files or uploading assets), and direct value change hooks (`on_value_change`) to detect and save toggle state.
- **Alternatives Considered**: Custom toggle buttons with container show/hide. Rejected because `ui.expansion` already handles keyboard accessibility, chevron transitions, and styling out of the box.

### 3. Explorer Section Persistence
- **Choice**: Store explorer state in `config.json` under `workspace_ui_state[workspace_slug]["expanded_sections"]` (list of strings, e.g., `["content", "resources"]`). Defaults to expanding `content` and `resources`.
- **Rationale**: `config.json` via `ConfigManager` is already the established store for user preferences and persistent settings (like `cover_size` and `recent_ebooks`). Persisting by workspace slug ensures each book maintains its own preferred view.
- **Alternatives Considered**: Storing in `metadata.json` inside the book folder. Rejected because UI expansion preferences are user-specific local preferences rather than book publication metadata.

### 4. Build Deliverable Serving (`dist/`)
- **Choice**: Add a secured endpoint `/api/workspace/dist/{file_path:path}` in `asset_server.py` with strict path traversal validation against `workspace.dist_dir`. For PDF, opening the URL with `new_tab=True` opens the browser's built-in PDF viewer. For EPUB, the endpoint sends `Content-Disposition: attachment` or `application/epub+zip`.
- **Rationale**: Uses native browser capabilities without adding heavyweight PDF or EPUB dependencies to pywebview.

### 5. Asset Preview Dialog
- **Choice**: Clicking an image in the `Assets` accordion opens a NiceGUI `ui.dialog` containing the rendered image (via `/assets/{filename}`), dimensions/size metadata, and a primary button that executes a lightweight client-side clipboard copy for `![{name}](assets/{filename})`.
- **Rationale**: Authors frequently need to reference images while writing in the editor. Instant copy-to-clipboard avoids typing paths manually.

## Component Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       NiceGUI Shell                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │ MultiFolderExplorer   │   │       VditorEditor        │  │
│  │ (file_tree.py)        │   │ (Instant Rendering mode)  │  │
│  ├───────────────────────┤   ├───────────────────────────┤  │
│  │ ▼ Content         [+] │   │                           │  │
│  │ ▼ Resources       [+] │──▶│ Renders active            │  │
│  │ ▼ Assets          [+] │   │ WorkspaceFile (content or │  │
│  │ ▼ Dist                │   │ resource, .md or .mmd)    │  │
│  └───────────────────────┘   └───────────────────────────┘  │
│              │                                              │
│              ▼                                              │
│  ┌───────────────────────┐   ┌───────────────────────────┐  │
│  │ AssetPreviewDialog    │   │  Dist Deliverable Action  │  │
│  │ - High-res preview    │   │  - PDF: Native view tab   │  │
│  │ - Copy Markdown link  │   │  - EPUB: Download         │  │
│  └───────────────────────┘   └───────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                    FastAPI Backend Core                     │
│  - EbookWorkspace: content/, resources/, assets/, dist/     │
│  - AssetServer: /assets/*, /api/workspace/dist/*            │
│  - ConfigManager: workspace_ui_state persistence            │
└─────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **[Risk] Active file switching between content/ and resources/** →
  *Mitigation*: `AppState.set_active_file()` updates `active_file` and syncs `active_chapter` to maintain backwards compatibility with existing UI listeners and status displays.
- **[Risk] High file count in assets/ or dist/ causing UI slowdown** →
  *Mitigation*: File list renders are lightweight flat lists with scrollable containers; `EbookWorkspace` uses fast directory scanning without deep recursion.
- **[Risk] Path traversal when viewing dist/ files** →
  *Mitigation*: Strict path validation checking `resolved_file.relative_to(workspace.dist_dir.resolve())` before serving files.
