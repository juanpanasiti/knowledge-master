## MODIFIED Requirements

### Requirement: Ebook Folder Structure Compliance
Each managed ebook project folder SHALL strictly conform to a standardized layout containing `metadata.json`, an `assets/` directory, a `content/` directory for published markdown files, a `resources/` directory for supplementary authoring materials, and an optional `dist/` directory for exported documents.

#### Scenario: Creating a new ebook project
- **WHEN** a user creates a new ebook with a title and author
- **THEN** the system generates the project directory under `~/knowledge-master/ebooks/<slug>/` containing `metadata.json`, an `assets/` directory with a default `cover.png`, a `content/` directory with an initial `1.md` file, and a `resources/` directory.

#### Scenario: Ensuring dist directory for exports
- **WHEN** an export operation or workspace initialization ensures folder structure
- **THEN** the system maintains the `dist/` directory inside the project root for storing generated EPUB and PDF files.

#### Scenario: Migrating existing workspace without resources folder
- **WHEN** an existing ebook project without a `resources/` folder is opened or validated
- **THEN** the system automatically creates the `resources/` directory within the ebook project root.

### Requirement: Natural Hierarchical Sorting of Chapters
The system SHALL sort markdown files located in the `content/` folder using natural hierarchical numerical sorting and SHALL display content titles in the sidebar without the `.md` extension under the Content section.

#### Scenario: Ordering files with numeric dot notation
- **WHEN** the `content/` folder contains files named `00 - Intro.md`, `1 - Chap.md`, `1.1 - Unit.md`, `1.2 - Unit.md`, and `1.10 - Unit.md`
- **THEN** the sidebar displays them in exact numerical order (`00 - Intro`, `1 - Chap`, `1.1 - Unit`, `1.2 - Unit`, `1.10 - Unit`) with `.md` hidden under the Content section.

## ADDED Requirements

### Requirement: Multi-Folder Explorer Structure and Section State Persistence
The system SHALL organize project files in the left sidebar into four distinct collapsible accordion sections: `Content`, `Resources`, `Assets`, and `Dist`, and SHALL persist the open/collapsed state of each accordion section per workspace.

#### Scenario: Rendering accordion explorer with saved state
- **WHEN** an ebook workspace is opened
- **THEN** the sidebar renders four collapsible sections (`Content`, `Resources`, `Assets`, and `Dist`) restoring each section's open or collapsed state from the saved configuration.

#### Scenario: Toggling accordion section
- **WHEN** the user collapses or expands an accordion section in the sidebar
- **THEN** the system immediately updates the UI and persists the new state for that workspace in configuration.

### Requirement: Resources Directory File Management
The system SHALL support creating, listing, renaming, reading, and deleting supplementary authoring files (including `.md`, `.mmd`, and plain text files) inside the active ebook's `resources/` directory, and SHALL exclude these files from final EPUB and PDF compilation.

#### Scenario: Creating a new resource file
- **WHEN** the user clicks the "New File" action in the Resources section and provides a filename (e.g., `flowchart.mmd` or `notes.md`)
- **THEN** the system creates the file inside `resources/`, updates the Resources file list, and selects the new file for editing.

#### Scenario: Export compilation isolation
- **WHEN** an EPUB or PDF export is executed
- **THEN** only markdown files in `content/` are compiled into the deliverable, and all files in `resources/` are excluded.
