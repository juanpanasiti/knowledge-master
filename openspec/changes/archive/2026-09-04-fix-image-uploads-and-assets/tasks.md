## 1. Core Asset Server Endpoints

- [x] 1.1 Register relative route aliases `/assets/{file_path:path}` and `/content/assets/{file_path:path}` in `src/ebook_editor/core/asset_server.py` and verify with automated pytest requests
- [x] 1.2 Add unit test cases in `tests/test_asset_server.py` for `/assets/` and `/content/assets/` resolving with 200 OK and valid image content types, and verify with `uv run pytest tests/test_asset_server.py`

## 2. Asynchronous NiceGUI 3 File Upload Handlers

- [x] 2.1 Update `MetadataPanelComponent._handle_cover_upload` in `src/ebook_editor/ui/components/metadata_panel.py` to asynchronously read `await event.file.read()`, safely handle notifications, and ensure `dialog.close()` in a `finally` block
- [x] 2.2 Update `WorkspaceView._handle_manual_image_insert` in `src/ebook_editor/ui/workspace_view.py` to asynchronously read `await event.file.read()`, generate relative markdown references (`./assets/<filename>`), safely notify, and ensure `dialog.close()` in a `finally` block
- [x] 2.3 Add tests in `tests/test_ui_layout.py` mocking NiceGUI 3 `FileUpload` events to verify asynchronous cover and asset reading without raising `AttributeError`

## 3. Vditor Instant Markdown Image Rendering

- [x] 3.1 Update `src/ebook_editor/ui/components/editor.py` upload configuration to invoke `vditor.insertMD()` on `upload.success` to trigger immediate Lute node compilation and render images inline
- [x] 3.2 Verify Vditor instant rendering via browser subagent or integration checks when images are uploaded

## 4. Versioning and Final Validation

- [x] 4.1 Bump package version in `pyproject.toml` from `0.1.1` to `0.1.2` and verify with `uv run pytest`
- [x] 4.2 Review `README.md` to ensure asset management instructions remain accurate
- [x] 4.3 Run all tests with `uv run pytest` to ensure complete suite passes with 0 failures
