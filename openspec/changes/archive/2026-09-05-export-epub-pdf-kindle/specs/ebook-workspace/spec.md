## MODIFIED Requirements

### Requirement: Ebook Folder Structure Compliance
Each managed ebook project folder SHALL strictly conform to a standardized layout containing `metadata.json`, an `assets/` directory, a `content/` directory for markdown files, and an optional `dist/` directory for exported documents.

#### Scenario: Creating a new ebook project
- **WHEN** a user creates a new ebook with a title and author
- **THEN** the system generates the project directory under `~/knowledge-master/ebooks/<slug>/` containing `metadata.json`, an `assets/` directory with a default `cover.png`, and a `content/` directory with an initial `1.md` file.

#### Scenario: Ensuring dist directory for exports
- **WHEN** an export operation or workspace initialization ensures folder structure
- **THEN** the system maintains the `dist/` directory inside the project root for storing generated EPUB and PDF files.

### Requirement: Metadata Schema Validation
The system SHALL validate and persist project metadata in `metadata.json` including title, author, description, cover image relative path, tags, publication state (`finished`), creation timestamp, and update timestamp.

#### Scenario: Updating project metadata
- **WHEN** the user edits the metadata fields in the metadata panel or toggles publication status in the export dialog and saves
- **THEN** the system updates `metadata.json` ensuring all fields comply with the schema (including `finished`), and sets `updated_at` to the current UTC timestamp.
