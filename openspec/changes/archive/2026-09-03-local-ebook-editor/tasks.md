## 1. Project Scaffolding and Dependencies

- [x] 1.1 Initialize `pyproject.toml` with `uv`, configuring Python 3.11+, dependencies (`nicegui`, `pywebview`, `pydantic>=2.0`, `gitpython`, `platformdirs`, `natsort`, `pytest`), and console script `knowledge-master = "ebook_editor.main:run"`, verifying installation with `uv sync`.
- [x] 1.2 Create package directory structure under `src/ebook_editor/` (`core/`, `ui/`, `ui/components/`, `static/`) and verify modules import cleanly.

## 2. Core Models, Workspace Management, and Git Service

- [x] 2.1 Implement `core/models.py` with Pydantic models for `EbookMetadata` and `AppSettings`, verifying serialization and validation with unit tests.
- [x] 2.2 Implement `core/config.py` managing `~/knowledge-master/config.json` initialization, recent ebooks list, and user preferences, verifying file creation on missing directory.
- [x] 2.3 Implement `core/workspace.py` handling ebook creation (`metadata.json`, `assets/cover.png`, `content/1.md`), discovery in `~/knowledge-master/ebooks/`, content listing with natural hierarchical sorting (`natsort`), and chapter CRUD (create, rename, delete), verifying with unit tests.
- [x] 2.4 Implement `core/git_service.py` wrapping `gitpython` with non-blocking checks for git binary and author identity, supporting repo init, status, stage/unstage, discard changes, commit, and log, verifying with unit tests on a temporary repository.

## 3. Dynamic Asset Serving and Vditor Integration

- [x] 3.1 Bundle offline Vditor distribution assets in `src/ebook_editor/static/vendor/vditor/` and verify local asset file existence and integrity.
- [x] 3.2 Implement dynamic asset route `/api/workspace/assets/{path:path}` and upload endpoint `/api/workspace/upload-asset` on NiceGUI's FastAPI application, verifying image serving and file upload security with unit tests.
- [x] 3.3 Create the Vditor NiceGUI component (`ui/components/editor.py`) configured for Instant Rendering (`ir`), dark theme default, debounced autosave (500ms), and clipboard/drag-and-drop image upload integration.

## 4. User Interface Implementation

- [x] 4.1 Implement `ui/dashboard.py` showing recent ebooks, auto-discovered ebooks in `~/knowledge-master/ebooks/`, "New Ebook" dialog with metadata inputs, and "Open Existing Ebook" directory picker, verifying state transitions.
- [x] 4.2 Implement `ui/components/file_tree.py` displaying the list of chapters with natural sorting and `.md` extensions hidden, including new chapter modal, rename, and delete actions.
- [x] 4.3 Implement `ui/components/metadata_panel.py` providing interactive form fields for title, author, description, tags, cover image preview, and cover image replacement.
- [x] 4.4 Implement `ui/components/git_panel.py` displaying repository status, stage/unstage buttons (individual and bulk), discard changes button, commit message field with commit button, recent commit history log, and disabled notice when Git is unconfigured.
- [x] 4.5 Assemble `ui/workspace_view.py` and `ui/state.py` linking sidebar file tree, central Vditor editor, status bar with word count and save indicator, metadata panel, and Git panel into a cohesive split-view layout.

## 5. System Integration, Packaging, and Verification

- [x] 5.1 Implement `main.py` entrypoint configuring NiceGUI in native mode (`native=True`) with window size 1280x800, custom application title, and theme synchronization.
- [x] 5.2 Create application icon at `assets/icon.png` and create root installer script `install.sh` performing `uv tool install --force --reinstall .`, generating `~/.local/share/applications/knowledge-master.desktop`, and updating desktop database.
- [x] 5.3 Execute comprehensive automated test suite (`uv run pytest`) and verify that `uv run knowledge-master` launches the application locally without errors.
- [x] 5.4 Execute `./install.sh` and verify global installation in `~/.local/bin/knowledge-master` and desktop launcher generation.
