## 1. Dependencies and Assets Setup

- [x] 1.1 Add `pypandoc>=1.16.2`, `weasyprint>=60.0`, and `python-dotenv>=1.0.0` to `pyproject.toml` dependencies and verify `uv lock` succeeds.
- [x] 1.2 Bundle export stylesheets (`epub.css`, `pdf.css`) and Lua filters (`line-numbers.lua`, `obsidian-callouts.lua`, `syntax-alias.lua`) into `src/ebook_editor/assets/export/` and verify all asset files exist.

## 2. Domain Models and Workspace Updates

- [x] 2.1 Update `EbookMetadata` in `src/ebook_editor/core/models.py` with `finished: bool = False` and update `AppSettings` with optional Kindle/SMTP fields, verifying serialization with unit tests in `tests/test_models.py`.
- [x] 2.2 Update `EbookWorkspace` in `src/ebook_editor/core/workspace.py` to manage the `<workspace>/dist` directory, verifying directory creation with unit tests in `tests/test_workspace.py`.

## 3. Core Export and Delivery Services

- [x] 3.1 Implement `KindleCredentials` and waterfall credential resolver in `src/ebook_editor/core/export/credentials.py` supporting `~/.config/ebook-maker/.env` and environment variables, verifying with unit tests in `tests/test_export.py`.
- [x] 3.2 Implement EPUB compilation in `src/ebook_editor/core/export/exporter.py` using Pandoc, bundled CSS, Lua filters, and natural chapter ordering, verifying output generation with unit tests.
- [x] 3.3 Implement A4 PDF compilation in `src/ebook_editor/core/export/exporter.py` using Pandoc HTML5 conversion and WeasyPrint, verifying output rendering with unit tests.
- [x] 3.4 Implement `KindleSender` in `src/ebook_editor/core/export/sender.py` to transmit EPUB attachments via SMTP TLS, verifying with mock SMTP unit tests.

## 4. UI Components and Workspace Integration

- [x] 4.1 Create `ExportDialog` component in `src/ebook_editor/ui/components/export_dialog.py` with publication toggle, EPUB/PDF generation actions, Kindle delivery action, and non-blocking `asyncio.to_thread` execution.
- [x] 4.2 Integrate the "Export" button and `ExportDialog` into the top navigation header of `WorkspaceView` in `src/ebook_editor/ui/workspace_view.py`.
- [x] 4.3 Add Kindle and SMTP status indicators to the Settings dialog in `src/ebook_editor/ui/dashboard.py`.

## 5. Testing, Documentation, and Final Validation

- [x] 5.1 Run full export test suite in `tests/test_export.py` covering EPUB, PDF, Kindle sender, and credential resolution with `uv run pytest tests/test_export.py`.
- [x] 5.2 Bump project version to `0.3.0` in `pyproject.toml` and verify version metadata.
- [x] 5.3 Review and update `README.md` to document EPUB/PDF export, Kindle transmission, and credential configuration.
- [x] 5.4 Execute complete test suite (`uv run pytest`) and perform final validation ensuring all acceptance criteria and proposal requirements are satisfied.
