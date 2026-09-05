# Proposal: EPUB and PDF Export with Send to Kindle Delivery

## Why

Knowledge Master provides editing and workspace management for Markdown ebooks, but authors currently lack the ability to export their work into standard portable formats directly from the app. By porting and enhancing the proven compilation and delivery workflows from `ebook-maker` (Pandoc EPUB generation, WeasyPrint PDF layout, and SMTP Kindle transmission), authors can generate formatted reading copies and publish them directly to their Kindle e-readers in a single click.

## User Impact

- Authors can open an "Export & Publish" dialog from the workspace navigation bar.
- Authors can toggle between Draft and Finished publication states to control automatic `[DRAFT]` title prefixes.
- Authors can compile their markdown chapters into a clean, styled `.epub` with Table of Contents and custom CSS.
- Authors can compile an A4 `.pdf` rendered with WeasyPrint, featuring a full-bleed cover and code syntax highlighting.
- Authors can transmit generated `.epub` files directly to their Kindle email via SMTP without leaving Knowledge Master.
- Existing credentials and environment variables in `~/.config/ebook-maker/.env` and system environment are automatically discovered with zero required reconfiguration.

## Goals

1. Implement headless core export services (`EbookExporter` and `KindleSender`) supporting EPUB generation, PDF generation, and SMTP delivery.
2. Embed the required export assets (styles `epub.css`, `pdf.css`, and Lua filters `line-numbers.lua`, `obsidian-callouts.lua`, `syntax-alias.lua`) within Knowledge Master.
3. Bundle and compile all markdown files in `content/` sorted in natural order (`natsort`), resolving `./assets/` image paths seamlessly.
4. Output generated files to a dedicated `<workspace>/dist/` directory inside each ebook project.
5. Create a dedicated "Export & Publish" modal dialog in `WorkspaceView` with non-blocking execution (`asyncio.to_thread`) and live status feedback.
6. Provide automatic credential resolution cascading from app settings, local `.env`, global `~/.config/ebook-maker/.env`, and system environment.

## Non-Goals

- Google Drive cloud backup/sync (out of scope for this change).
- Custom CSS editing interface within the app (bundled stylesheets and filters will be used).
- Mobi or AZW3 conversion (Amazon Kindle Personal Documents Service natively accepts EPUB files).

## Capabilities

### New Capabilities
- `ebook-export`: Complete export pipeline covering Pandoc EPUB compilation, WeasyPrint PDF rendering, SMTP Kindle delivery, and non-blocking export UI dialog.

### Modified Capabilities
- `ebook-workspace`: Extend `EbookMetadata` with `finished` flag and ensure `dist/` export folder lifecycle is managed.

## Impact

- **Dependencies**: Add `pypandoc>=1.16.2`, `weasyprint>=60.0`, and `python-dotenv>=1.0.0` to `pyproject.toml`.
- **System Requirements**: Requires system `pandoc` (already installed at `/usr/bin/pandoc`) and standard system graphic libraries for WeasyPrint (`pango`, `cairo`).
- **Data Models**: Add `finished: bool = False` to `EbookMetadata` in `src/ebook_editor/core/models.py`.
- **UI Components**: Add "Export" action button in `WorkspaceView` header and a new `ExportDialog` component.
- **SemVer**: Minor version bump from `0.2.0` to `0.3.0` due to major feature addition without breaking existing workspace data.
