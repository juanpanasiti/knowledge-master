# Proposal: Multi-Folder Workspace Explorer and Resources Management

## Why

Currently, the sidebar file tree is exclusively titled "Chapters" and restricted to files inside `content/`. However, authors create ebooks that contain non-chapter content (prefaces, appendices, units, modular sections) and frequently work with supplementary authoring materials such as Mermaid diagram sources (`.mmd`), research notes, and draft text that should not be automatically compiled into the final published ebook. Additionally, authors have no direct visibility into their `assets/` (images, covers) or generated `dist/` builds (EPUB, PDF) from the workspace sidebar, forcing them to leave the editor to inspect exported files or verify images.

Organizing the sidebar into collapsible accordion sections—`Content`, `Resources`, `Assets`, and `Dist`—with persistent expansion state, direct editor support for editing resource files, inline asset preview with quick Markdown link insertion, and direct viewing/downloading of generated builds significantly streamlines the technical authoring workflow.

## What Changes

- **Renaming "Chapters" to "Content"**: Update sidebar header, UI labels, and internal references from "Chapters" to "Content" to accurately represent all modular markdown files forming the book body.
- **Introduction of `resources/` Directory**: Standardize a new `resources/` folder in each ebook project workspace for authoring materials (e.g., Mermaid diagram sources `.mmd`, research notes `.md`/`.txt`, raw data) excluded from EPUB/PDF export compilation.
- **Editable Resources**: Enable opening and editing markdown, mermaid, and plain-text files located in `resources/` in the Vditor editor while keeping them isolated from book export compilation.
- **Multi-Section Accordion Explorer**: Restructure the left sidebar into 4 collapsible accordion sections:
  - `Content`: Markdown files forming the book chapters/sections (CRUD, reordering, active editor selection).
  - `Resources`: Supplementary files (`.md`, `.mmd`, `.txt`) with CRUD and editor opening.
  - `Assets`: Media assets (`cover.png`, diagram exports, `.png`, `.jpg`, `.svg`) with upload, deletion, and preview.
  - `Dist`: Generated build deliverables (`.epub`, `.pdf`) showing file size, timestamp, and actions.
- **Persistent Accordion State**: Persist the expanded/collapsed state of each accordion section per workspace in user configuration or local settings so author preference is preserved across app restarts and project switches.
- **Asset Preview Modal**: Clicking an asset displays a modal preview with full-resolution display and a 1-click button to copy its Markdown reference (`![alt](assets/filename.png)`) to the clipboard.
- **Dist Build Interaction**: Clicking or selecting a generated PDF in `dist/` opens it directly in a browser tab using the native browser PDF viewer, and clicking an EPUB triggers download or system default reader launch.

## Capabilities

### Modified Capabilities
- `ebook-workspace`: Standardize `resources/` directory creation in project layout; update workspace models and directory listings to support multi-folder discovery (`content/`, `resources/`, `assets/`, `dist/`); persist explorer accordion states per workspace.
- `markdown-editor`: Support selecting and editing files from `resources/` alongside `content/`; provide inline asset preview modal with Markdown link generation; enable opening/downloading build outputs from `dist/`.

## Impact

- **Workspace File Structure**: `EbookWorkspace.ensure_structure()` ensures `resources/` directory exists alongside `content/`, `assets/`, and `dist/`. Existing workspaces automatically gain the `resources/` directory on open.
- **UI Components**:
  - `FileTreeComponent` refactored into an accordion-based multi-folder explorer component.
  - `AppState` updated to track active editable file (supporting both `content/` and `resources/` files).
  - `WorkspaceView` and `ConfigManager` updated to persist accordion open/closed preferences.
- **Asset Routes & Endpoints**: Add route endpoints to serve and download files from `dist/` and `resources/` securely with path traversal guards.
- **Backward Compatibility**: Fully backward compatible; existing `content/`, `assets/`, and `dist/` structures remain unchanged, and export logic continues to bundle only files from `content/`.
- **SemVer Impact**: Minor feature increment (0.2.0 or 0.1.X).
