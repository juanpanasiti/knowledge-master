## Context

Knowledge Master is a standalone local ebook management and editing tool built with Python and NiceGUI. See `proposal.md` for background and problem motivation.

The project requires a native desktop window experience without running in a browser tab, zero reliance on external cloud services or online CDNs for core editing, and strict local directory management tailored for markdown-based authoring.

## Goals / Non-Goals

**Goals:**
- Provide a clean, modular Python codebase managed by `uv` with strict type hints and Pydantic v2 data models.
- Run seamlessly in native desktop mode (`ui.run(native=True)`) using `pywebview`.
- Integrate Vditor with locally bundled assets for instant rendering (live preview) markdown editing, offline capability, and dark mode styling by default.
- Support debounced autosave (500ms) with visible status indication.
- Serve local images from each project's `assets/` directory dynamically via a FastAPI endpoint without restarting routes on ebook change.
- Provide a robust, non-blocking Git version control panel with graceful degradation if Git is unconfigured.
- Provide a single-command global installer and updater script (`install.sh`) configuring `uv tool` and OS desktop integration (`.desktop`).

**Non-Goals:**
- Nested subdirectories inside `content/` (all markdown files reside flatly within `content/`).
- Multi-format compilation or exporting (PDF, EPUB, DOCX) in this initial release.
- Cloud syncing or multi-user collaborative editing.

## Decisions

### 1. Application Directory & User State
- **Decision**: Establish `~/knowledge-master/` as the single user-facing directory on the system.
  - `~/knowledge-master/config.json`: Managed via Pydantic model `AppSettings`, tracking recent ebooks, last active ebook, theme preference, and UI state.
  - `~/knowledge-master/ebooks/`: Default directory where new ebooks are generated and auto-discovered.
- **Alternatives considered**: Standard hidden XDG directories (`~/.config/knowledge-master` and `~/.local/share`).
  - *Rationale*: Placing the folder visibly at `~/knowledge-master/` allows authors to easily locate, inspect, and back up their markdown files and assets directly using standard OS file managers.

### 2. Ebook Project Schema & Validation
- **Decision**: Enforce an isolated directory structure per ebook:
  ```
  /ebook-directory/
  ├── .git/            (Optional)
  ├── .gitignore       (Created when Git initialized)
  ├── metadata.json    (Validated via Pydantic EbookMetadata)
  ├── assets/          (Holds cover.png and inserted images)
  └── content/         (Holds flat markdown files)
  ```
  `metadata.json` schema:
  - `title`: str
  - `author`: str
  - `description`: str = ""
  - `cover_path`: str = "assets/cover.png"
  - `tags`: list[str] = []
  - `created_at`: datetime
  - `updated_at`: datetime
- **Alternatives considered**: Storing markdown files directly in the root alongside `assets/`.
  - *Rationale*: A dedicated `content/` folder prevents cluttering the ebook root with dozens of chapter files alongside metadata and Git structures.

### 3. Hierarchical Natural Sorting
- **Decision**: Sort files in `content/` using natural multi-segment numeric sorting (using `natsort` or numerical dot-split logic).
- **Format**: Supports filenames like `00 - Intro.md`, `1 - Overview.md`, `1.1 - Unit.md`, `1.1.1 - Detail.md`, `1.10 - Advanced.md`.
  - The UI sidebar strips the `.md` extension, presenting clean titles like `1.1.1 - Detail`.
- **Alternatives considered**: Standard lexical ASCII sorting.
  - *Rationale*: Lexical sorting places `1.10` before `1.2`, breaking the author's logical book outline.

### 4. Vditor Integration & Offline Asset Bundling
- **Decision**: Bundle Vditor's distribution files (JS, CSS, icons, fonts) directly within `src/ebook_editor/static/vendor/vditor/` and serve them locally through NiceGUI static mounts.
- **Render Mode**: Instant Rendering (`ir`) mode provides an inline live-preview WYSIWYG experience identical to Obsidian and Typora.
- **Theme**: Dark theme initialized by default (`theme: "dark"`, `preview.theme: "dark"`), dynamically synchronized with NiceGUI's dark mode toggle.
- **Alternatives considered**: EasyMDE or CDN-loaded Vditor.
  - *Rationale*: EasyMDE lacks true inline WYSIWYG; CDN-based loading breaks offline functionality in a desktop application.

### 5. Dynamic Asset Route
- **Decision**: Register a FastAPI endpoint on NiceGUI's underlying Starlette application:
  `GET /api/workspace/assets/{path:path}`
  When invoked, it resolves `{path}` safely against the active ebook's `assets/` directory and returns a `FileResponse`.
- **Image Insertion**:
  - Drag & drop and paste events in Vditor intercept image files, upload them via a POST endpoint (`/api/workspace/upload-asset`), save them into `assets/`, and insert `![alt](./assets/<filename>)` into the document.
  - An interactive NiceGUI dialog also allows picking local image files.
- **Alternatives considered**: Re-mounting `app.add_static_files('/assets', ...)` on project switches.
  - *Rationale*: FastAPI routing tables do not support dynamic unmounting and remounting cleanly at runtime.

### 6. Git Service Architecture & Graceful Degradation
- **Decision**: Encapsulate all Git interactions in `GitService` wrapping `GitPython`.
  - Checks for the presence of the system `git` binary and checks if `user.name` and `user.email` are set.
  - If missing, Git capabilities are disabled cleanly in the UI with an informative banner.
  - Supported operations: `git init` (with standard `.gitignore`), `git status`, stage/unstage file, stage/unstage all, discard changes (`checkout --`), commit, and commit log (`log -n 20`).
- **Alternatives considered**: Requiring Git as an absolute hard dependency for app startup.
  - *Rationale*: Authors should be able to write and organize books without needing Git installed.

### 7. Global Deployment via `uv tool`
- **Decision**: Configure `pyproject.toml` with `[project.scripts] knowledge-master = "ebook_editor.main:run"` and provide `install.sh` in the project root:
  1. Executes `uv tool install --force --reinstall .`
  2. Copies or creates desktop launcher `~/.local/share/applications/knowledge-master.desktop`
  3. Installs app icon in `~/.local/share/icons/hicolor/scalable/apps/`
- **Alternatives considered**: PyInstaller standalone binary only.
  - *Rationale*: `uv tool` provides instant installation and rebuild times for local developers while allowing PyInstaller for zero-dependency redistribution when needed.

## Risks / Trade-offs

- **[Risk] pywebview dependencies on Linux**: If WebKitGTK is missing on Linux, `native=True` can fail to launch.
  - *Mitigation*: Catch pywebview initialization errors in `main.py` and print a helpful terminal error instructing the user to install `libwebkit2gtk-4.0` / `libwebkit2gtk-4.1`.
- **[Risk] Vditor large bundle size**: Bundling all Vditor distribution files increases repository footprint.
  - *Mitigation*: Include only required distribution files (minified JS, CSS, fonts, and core themes), keeping package footprint lightweight.
- **[Risk] Autosave race conditions**: Writing to disk frequently during rapid typing could cause file contention or partial writes.
  - *Mitigation*: Use 500ms debouncing, write atomically via temporary file replacement or asynchronous disk I/O, and display visual feedback in the status bar.
