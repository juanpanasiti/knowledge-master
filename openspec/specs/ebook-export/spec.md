# Ebook Export Specification

## Purpose

Provides standalone and integrated export capabilities to compile markdown ebook chapters into styled EPUB and A4 PDF documents, and transmit EPUB files directly to Kindle devices via SMTP email.

## Requirements

### Requirement: EPUB Compilation from Workspace Chapters
The system SHALL compile all markdown chapter files located in the active ebook's `content/` directory into a single styled EPUB document using Pandoc, embedding the book cover, Table of Contents up to level 2, custom e-reader CSS, and syntax/callout Lua filters.

#### Scenario: Compiling draft EPUB
- **WHEN** the user initiates EPUB export on an ebook with `finished` set to false
- **THEN** the system generates `<workspace>/dist/[DRAFT] <title>.epub` containing all chapters concatenated in natural sort order with cover and TOC included.

#### Scenario: Compiling finalized EPUB
- **WHEN** the user initiates EPUB export on an ebook with `finished` set to true
- **THEN** the system generates `<workspace>/dist/<title>.epub` without the `[DRAFT]` prefix.

#### Scenario: Resolving embedded chapter assets in EPUB
- **WHEN** a chapter contains image references formatted as `./assets/<image>.png` or `assets/<image>.png`
- **THEN** Pandoc resolves the images relative to the workspace root and packages them into the output EPUB.

#### Scenario: Missing markdown chapters for EPUB
- **WHEN** EPUB export is initiated on a workspace with zero markdown files in `content/`
- **THEN** the system aborts compilation and raises a descriptive error notification indicating that no chapter files exist.

### Requirement: A4 PDF Compilation with WeasyPrint
The system SHALL compile markdown chapters into HTML5 via Pandoc, inject full-bleed cover image markup and overrides, apply print-ready CSS styles, and render an A4 PDF document using WeasyPrint into `<workspace>/dist/`.

#### Scenario: Compiling draft PDF
- **WHEN** the user initiates PDF export on an ebook with `finished` set to false
- **THEN** the system renders `<workspace>/dist/[DRAFT] <title>.pdf` with full-bleed cover, page numbers, and custom typography.

#### Scenario: Compiling finalized PDF
- **WHEN** the user initiates PDF export on an ebook with `finished` set to true
- **THEN** the system renders `<workspace>/dist/<title>.pdf` without the `[DRAFT]` prefix.

#### Scenario: PDF compilation error handling
- **WHEN** WeasyPrint or Pandoc encounters an unrecoverable rendering or syntax error
- **THEN** the system captures the failure, ensures temporary artifacts are cleaned up, and presents a user-friendly error message.

### Requirement: Send EPUB to Kindle Device via SMTP
The system SHALL send the compiled EPUB file to an authorized Kindle email address as a MIME attachment (`application/epub+zip`) through an authenticated SMTP server using STARTTLS encryption.

#### Scenario: Successful transmission to Kindle
- **WHEN** the user clicks "Send to Kindle" and valid SMTP credentials and a Kindle email address are configured
- **THEN** the system compiles the EPUB if missing, attaches it to an email message, delivers it via SMTP TLS, and notifies the user of successful delivery.

#### Scenario: Missing email credentials
- **WHEN** the user attempts to send an EPUB to Kindle but `SMTP_USER`, `SMTP_PASSWORD`, or `KINDLE_EMAIL` is unconfigured
- **THEN** the system halts transmission and informs the user which credential settings are missing.

#### Scenario: SMTP authentication failure
- **WHEN** the SMTP server rejects authentication due to invalid credentials
- **THEN** the system catches the authentication exception and reports an authentication error without crashing the application.

### Requirement: Credential and Configuration Resolution Cascade
The system SHALL resolve Kindle and SMTP delivery settings in order of precedence: application settings in `config.json`, local `.env`, global `~/.config/ebook-maker/.env`, and system environment variables.

#### Scenario: Fallback to global ebook-maker configuration
- **WHEN** Knowledge Master has no explicit SMTP settings in `config.json` but `~/.config/ebook-maker/.env` exists with valid credentials
- **THEN** the system automatically loads `KINDLE_EMAIL`, `SMTP_USER`, and `SMTP_PASSWORD` from the global `ebook-maker` environment file.

#### Scenario: Overriding credentials via environment or config
- **WHEN** the user specifies custom credentials in Knowledge Master settings
- **THEN** the custom configuration takes precedence over global fallback files.

### Requirement: Non-Blocking Export UI Modal Dialog
The system SHALL provide an "Export & Publish" button in the `WorkspaceView` navigation bar that displays a modal dialog with publication status toggle, EPUB generation button, PDF generation button, Send to Kindle button, and non-blocking asynchronous execution.

#### Scenario: Opening export dialog
- **WHEN** the user clicks the "Export" button in the active workspace header
- **THEN** the system opens the "Export & Publish" dialog showing current publication status (Draft/Finished), configured Kindle target email, and compilation actions.

#### Scenario: Non-blocking background compilation
- **WHEN** the user clicks "Generate EPUB" or "Generate PDF"
- **THEN** the UI displays an active progress indicator while the compilation runs in a background thread, keeping the application interactive until completion.
