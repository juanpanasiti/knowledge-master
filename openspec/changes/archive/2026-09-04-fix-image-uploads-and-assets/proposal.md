## Why

In NiceGUI 3+, `UploadEventArguments` changed its internal structure from a synchronous `.content` property to an asynchronous `.file: FileUpload` instance (`await file.read()`). When users attempted to change an eBook's cover or insert an image via the toolbar dialog, an unhandled `AttributeError: 'UploadEventArguments' object has no attribute 'content'` was raised, preventing files from saving and freezing upload dialogs at 100%.

Additionally, standard Markdown files reference images using relative paths such as `![alt](./assets/image.png)`. Because the FastAPI backend only registered `/api/workspace/assets/{path}`, requests to `/assets/{path}` returned `404 Not Found`. Furthermore, when images were uploaded via Vditor's toolbar, default Vditor behavior pasted raw markdown text without immediately compiling the node through Lute into an `<img>` tag.

This change fixes asset routing, ensures full compatibility with NiceGUI 3 upload events, and enables instant rendering of newly uploaded images in Vditor.

## What Changes

- **NiceGUI 3 Asynchronous File Upload**: Updated `MetadataPanelComponent._handle_cover_upload` and `WorkspaceView._handle_manual_image_insert` to extract file bytes via `await event.file.read()` with backwards-compatible fallback, and guaranteed dialog dismissal via `finally: dialog.close()`.
- **Relative Asset Routes in FastAPI**: Registered route aliases `/assets/{file_path:path}` and `/content/assets/{file_path:path}` on the FastAPI app so that standard relative image links (`./assets/...` or `assets/...`) resolve with `200 OK`.
- **Immediate Vditor Image Rendering**: Added an `upload.success` callback in `VditorEditor` that invokes `vditor.insertMD()` to immediately parse and render uploaded images using Lute instead of inserting plain text.
- **Automated Test Coverage**: Added tests in `tests/test_asset_server.py` and `tests/test_ui_layout.py` verifying `/assets/` routing and NiceGUI 3 `FileUpload` handling.

## Capabilities

### Modified Capabilities
- `ebook-workspace`: Asset serving must support relative paths (`/assets/...`) alongside canonical paths, and upload handlers must process NiceGUI 3 `FileUpload` streams without crashing dialog state.
- `markdown-editor`: Vditor must immediately render newly uploaded images as visual elements in Instant Rendering mode.

## Impact

- Affected Code:
  - `src/ebook_editor/core/asset_server.py`: Added relative route endpoints.
  - `src/ebook_editor/ui/components/metadata_panel.py`: Async cover upload handler and dialog close guard.
  - `src/ebook_editor/ui/workspace_view.py`: Async image upload handler and canonical URL formatting.
  - `src/ebook_editor/ui/components/editor.py`: Added `upload.success` callback.
  - `tests/test_asset_server.py`: Relative route test coverage.
  - `tests/test_ui_layout.py`: Asynchronous upload unit tests.
- Dependencies: No new dependencies; uses existing FastAPI, NiceGUI 3, and Pytest libraries.
- SemVer: Patch release (`0.1.2`).
