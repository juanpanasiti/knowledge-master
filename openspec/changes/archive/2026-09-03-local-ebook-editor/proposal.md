## Why

Writing and managing markdown-based ebooks locally currently requires either general-purpose text editors lacking structured project workflows or heavy Electron-based tools with high memory consumption and disjointed asset pipelines.
This project introduces Knowledge Master, a native desktop application built with Python and NiceGUI, providing an Obsidian-inspired instant rendering WYSIWYG writing experience with lightweight, local-first ebook workspace management, embedded asset serving, and non-blocking Git version control.

## What Changes

- Create a native desktop application powered by NiceGUI (`native=True` via `pywebview`).
- Establish a user workspace root at `~/knowledge-master/` containing application configuration (`config.json`) and an `ebooks/` directory.
- Define and enforce an isolated, strict disk structure for each ebook (`metadata.json`, `assets/`, and `content/` with flat markdown files).
- Implement hierarchical natural sorting for markdown files (e.g., `00 - ...`, `1`, `1.1`, `1.1.1`, `1.2`, `2`) while hiding the `.md` extension in the sidebar navigation.
- Embed the Vditor editor with local bundled offline assets, offering Instant Rendering (Live Preview), dark theme by default, theme toggling, and debounced autosave.
- Support seamless image insertion via clipboard paste (`Ctrl+V`), drag & drop, and manual file picker, automatically saving images to `assets/` and referencing them via relative links.
- Serve workspace media assets via a dynamic NiceGUI / FastAPI endpoint (`/api/workspace/assets/{path}`).
- Provide interactive project metadata editing and cover image preview/replacement (`assets/cover.png`).
- Implement a graceful, non-blocking Git version control panel supporting staging, unstaging (individual and bulk), change discarding, commit authoring, and commit history.
- Provide an automated global installer script (`install.sh`) utilizing `uv tool` and registering the desktop application launcher (`.desktop`) and icon.

## Capabilities

### New Capabilities
- `ebook-workspace`: Creation, opening, and management of ebook projects, metadata schemas, flat `content/` markdown storage, and hierarchical natural sorting of chapters.
- `markdown-editor`: Native window WYSIWYG editing powered by Vditor with offline bundled assets, dark theme default, debounced autosave, and local image insertion and serving.
- `git-integration`: Non-blocking local Git management with graceful degradation, staging/unstaging, discard changes, commit creation, and commit history log.
- `system-packaging`: Global CLI and desktop installation workflow via `install.sh`, `uv tool`, and `.desktop` application menu integration.

### Modified Capabilities
<!-- None. This is a greenfield project. -->

## Impact

- **New Dependencies**: `nicegui`, `pywebview`, `pydantic>=2.0`, `gitpython`, `platformdirs`, `natsort`.
- **System Requirements**: Python 3.11+, `uv`, local GTK/WebKitGTK or webview runtime for `pywebview`.
- **User Filesystem**: Manages state in `~/knowledge-master/` and installs executable entrypoint `knowledge-master` into `~/.local/bin/`.
