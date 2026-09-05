# Design: EPUB and PDF Export with Send to Kindle Delivery

## Context

Knowledge Master manages ebook projects consisting of `metadata.json`, a `content/` folder with sorted Markdown chapters, and an `assets/` folder containing images and `cover.png`. In `ebook-maker`, conversion routines rely on `pypandoc` for EPUB generation (with custom CSS and Lua filters), `weasyprint` for A4 PDF rendering (via Pandoc HTML5 conversion), and `smtplib` for delivering the EPUB to a Kindle address.

This design brings these capabilities into Knowledge Master as headless core services under `ebook_editor.core.export`, bundles the required CSS and Lua assets into the package distribution, resolves credentials transparently, and presents a non-blocking "Export & Publish" modal dialog in the UI.

## Goals / Non-Goals

**Goals:**
- Provide headless export services: `EbookExporter` for EPUB and PDF generation, and `KindleSender` for email transmission.
- Bundle asset files (`epub.css`, `pdf.css`, `line-numbers.lua`, `obsidian-callouts.lua`, `syntax-alias.lua`) within `src/ebook_editor/assets/export/`.
- Ensure all subprocess calls (Pandoc) and heavy rendering (WeasyPrint) as well as SMTP connections execute in worker threads (`asyncio.to_thread`) to prevent blocking the NiceGUI event loop.
- Save generated outputs in `<workspace>/dist/` with filename prefixes honoring publication state (`[DRAFT] <title>.<ext>` or `<title>.<ext>`).
- Implement a waterfall credential resolver: App Settings → Local `.env` → Global `~/.config/ebook-maker/.env` → `os.environ`.
- Provide a clean, modern "Export & Publish" dialog in `WorkspaceView`.

**Non-Goals:**
- Custom template editor or custom CSS overrides per ebook (bundled stylesheets cover e-reader and A4 requirements).
- Direct cloud storage integration (Google Drive, Dropbox) in this change.

## Architecture & Component Breakdown

```
┌────────────────────────────────────────────────────────────────────────┐
│                              NiceGUI UI                                │
│                                                                        │
│   WorkspaceView (Header)                                               │
│         │                                                              │
│         ▼                                                              │
│   ExportDialog (UI Component)                                          │
│   ├── Publication State Toggle (Draft / Finished)                      │
│   ├── "Generate EPUB" Button (with progress spinner & open button)     │
│   ├── "Generate PDF" Button (with progress spinner & open button)      │
│   └── "Send to Kindle" Button (validates credentials & sends)          │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ asyncio.to_thread()
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Core Export Services                            │
│                                                                        │
│   ┌──────────────────────────────────┐  ┌──────────────────────────┐   │
│   │          EbookExporter           │  │       KindleSender       │   │
│   ├──────────────────────────────────┤  ├──────────────────────────┤   │
│   │ • compile_epub(ws) -> Path       │  │ • send_to_kindle(epub)   │   │
│   │ • compile_pdf(ws) -> Path        │  │ • get_credentials()      │   │
│   │ • _collect_markdown_files()      │  │ • validate()             │   │
│   │ • _get_output_filename()         │  │                          │   │
│   └─────────────────┬────────────────┘  └─────────────┬────────────┘   │
│                     │                                 │                │
│                     ▼                                 ▼                │
│             Assets / Bundled                   SMTP (Gmail / TLS)      │
│             ├── epub.css                       smtp.gmail.com:587      │
│             ├── pdf.css                                                │
│             └── *.lua filters                                          │
└─────────────────────┼─────────────────────────────────┼────────────────┘
                      ▼                                 ▼
             <workspace>/dist/                  Kindle Document Service
             ├── [DRAFT] Title.epub
             └── [DRAFT] Title.pdf
```

### 1. Data Models (`src/ebook_editor/core/models.py`)
- **`EbookMetadata`**:
  Add `finished: bool = Field(default=False, description="Whether the ebook is finalized for publication")`.
  When `finished` is False, generated filenames use the prefix `[DRAFT] <title>.<ext>`. When True, prefix is omitted.
- **`AppSettings`**:
  Add optional email and Kindle configuration fields:
  ```python
  kindle_email: str | None = None
  smtp_user: str | None = None
  smtp_password: str | None = None
  smtp_server: str = "smtp.gmail.com"
  smtp_port: int = 587
  ```

### 2. Credential Resolution (`src/ebook_editor/core/export/credentials.py`)
To ensure seamless integration with the user's existing setup, credentials resolve through a prioritized cascade:
1. `AppSettings` in `~/knowledge-master/config.json`
2. `.env` in the current working directory or `~/knowledge-master/.env`
3. Global `~/.config/ebook-maker/.env` (reusing existing credentials without re-prompting)
4. System environment variables (`KINDLE_EMAIL`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`)

### 3. Core Exporter (`src/ebook_editor/core/export/exporter.py`)
- **`compile_epub(workspace: EbookWorkspace) -> Path`**:
  - Ensures `<workspace>/dist` directory exists.
  - Concatenates markdown files from `workspace.content_dir` sorted with `natsorted`.
  - Configures Pandoc arguments:
    - `--from=markdown+markdown_in_html_blocks`
    - `--highlight-style=tango`
    - `--toc`, `--toc-depth=2`
    - `--resource-path=<workspace.root>` (allowing `./assets/image.png` and `assets/image.png` to resolve)
    - `--epub-cover-image=<workspace.assets_dir>/cover.png` (if exists)
    - Bundled CSS (`epub.css`) and Lua filters (`line-numbers.lua`, `obsidian-callouts.lua`, `syntax-alias.lua`).
  - Calls `pypandoc.convert_file()` to output `<workspace>/dist/<filename>.epub`.
- **`compile_pdf(workspace: EbookWorkspace) -> Path`**:
  - Converts markdown files into HTML5 via `pypandoc` with `--standalone` and `--embed-resources`.
  - Injects full-bleed cover markup and `@page :first { size: A4; margin: 0; }` style into the HTML.
  - Passes bundled `pdf.css` and base URL `<workspace.root>` to `weasyprint.HTML().write_pdf()`.
  - Outputs `<workspace>/dist/<filename>.pdf`.

### 4. Kindle Sender (`src/ebook_editor/core/export/sender.py`)
- **`send_to_kindle(epub_path: Path, credentials: KindleCredentials) -> None`**:
  - Validates `kindle_email`, `smtp_user`, and `smtp_password`.
  - Constructs `EmailMessage` with subject `"Sent from Knowledge Master"`.
  - Attaches EPUB file with MIME type `application/epub+zip`.
  - Connects to SMTP host (`smtp.gmail.com:587`), issues STARTTLS, authenticates, and sends message.

### 5. UI Integration: Export Modal Dialog (`src/ebook_editor/ui/components/export_dialog.py`)
- Accessible from a new "Export" button (`icon="ios_share"`) in the `WorkspaceView` top header.
- Presents:
  - Publication Status Toggle: "Draft" vs "Finished" (persists to `metadata.json`).
  - EPUB Section: "Generate EPUB" button + status/last built timestamp + "Open in Folder" / "Download" action.
  - PDF Section: "Generate PDF" button + status/last built timestamp + "Open in Folder" / "Download" action.
  - Kindle Section: Displays target Kindle email and "Send to Kindle" button.
  - Async worker wrappers: Buttons trigger async tasks using `await asyncio.to_thread(...)`, disabling buttons during processing and rendering a spinner with descriptive notifications on completion.

## Decisions

### Decision 1: Dedicated `dist/` folder instead of `ebooks/`
- **Rationale**: Ebook workspaces often live inside `~/knowledge-master/ebooks/<slug>/`. Creating an `ebooks/` folder inside would lead to redundant paths (`.../ebooks/<slug>/ebooks/`). `dist/` is an industry standard convention for compiled distributable artifacts.
- **Alternatives considered**: `output/`, `build/`. `dist/` was selected for clarity.

### Decision 2: Automatic credential fallback to `~/.config/ebook-maker/.env`
- **Rationale**: The user already maintains working Kindle and Gmail credentials in `~/.config/ebook-maker/.env`. By automatically reading this file as a fallback, the feature works immediately with zero setup required.
- **Alternatives considered**: Requiring manual re-entry in a UI dialog. Rejected as unnecessary friction.

### Decision 3: Background thread execution via `asyncio.to_thread`
- **Rationale**: Pandoc compilation and WeasyPrint rendering take between 2 and 8 seconds of heavy CPU and subprocess execution. Running them on the main thread would freeze the NiceGUI/pywebview window. `asyncio.to_thread` delegates the synchronous work to Python's default thread pool, keeping the UI responsive.
- **Alternatives considered**: Separate worker process via Celery or multiprocessing. Overkill for a local desktop tool; thread pool is standard for I/O and subprocess coordination in Python 3.11+.

## Risks / Trade-offs

- **[System Pandoc requirement]** → Pandoc must be present on the host system.
  *Mitigation*: Verify Pandoc presence at startup or before export and display an alert with installation instructions if missing. (Pandoc 3.1.3 is already verified present on this machine).
- **[WeasyPrint shared library dependencies]** → WeasyPrint requires Pango and Cairo C-libraries.
  *Mitigation*: `ebook-maker` already uses WeasyPrint 68 successfully on this machine. If an import error occurs, report clear system package requirements.
- **[Large image rendering in PDF]** → High-resolution images could slow down WeasyPrint.
  *Mitigation*: Pandoc processes images and WeasyPrint scales them within page margins defined in `pdf.css`.
- **[SMTP authentication failure]** → User might supply an incorrect App Password or change Google account security settings.
  *Mitigation*: Catch `smtplib.SMTPAuthenticationError` and provide a clear error message explaining the need for a 16-character Gmail App Password.
