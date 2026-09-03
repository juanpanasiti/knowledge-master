# Ebook Workspace Specification

## Purpose

Provides local-first ebook workspace discovery, creation, metadata management, and content organization with natural hierarchical sorting.

## Requirements

### Requirement: Central User Workspace Directory
The system SHALL initialize and maintain a dedicated root directory at `~/knowledge-master/` containing `config.json` and an `ebooks/` subfolder.

#### Scenario: First run workspace initialization
- **WHEN** the application starts and `~/knowledge-master/` does not exist
- **THEN** the system creates `~/knowledge-master/` and `~/knowledge-master/ebooks/` and generates a default `config.json` file.

### Requirement: Ebook Folder Structure Compliance
Each managed ebook project folder SHALL strictly conform to a standardized layout containing `metadata.json`, an `assets/` directory, and a `content/` directory for markdown files.

#### Scenario: Creating a new ebook project
- **WHEN** a user creates a new ebook with a title and author
- **THEN** the system generates the project directory under `~/knowledge-master/ebooks/<slug>/` containing `metadata.json`, an `assets/` directory with a default `cover.png`, and a `content/` directory with an initial `1.md` file.

### Requirement: Metadata Schema Validation
The system SHALL validate and persist project metadata in `metadata.json` including title, author, description, cover image relative path, tags, creation timestamp, and update timestamp.

#### Scenario: Updating project metadata
- **WHEN** the user edits the metadata fields in the metadata panel and saves
- **THEN** the system updates `metadata.json` ensuring all fields comply with the schema and sets `updated_at` to the current UTC timestamp.

### Requirement: Natural Hierarchical Sorting of Chapters
The system SHALL sort markdown files located in the `content/` folder using natural hierarchical numerical sorting and SHALL display chapter titles in the sidebar without the `.md` extension.

#### Scenario: Ordering files with numeric dot notation
- **WHEN** the `content/` folder contains files named `00 - Intro.md`, `1 - Chap.md`, `1.1 - Unit.md`, `1.2 - Unit.md`, and `1.10 - Unit.md`
- **THEN** the sidebar displays them in exact numerical order (`00 - Intro`, `1 - Chap`, `1.1 - Unit`, `1.2 - Unit`, `1.10 - Unit`) with `.md` hidden.

### Requirement: Markdown File CRUD Operations
The system SHALL allow users to create new markdown files, rename existing files, and delete files inside the active ebook's `content/` directory.

#### Scenario: Creating a new chapter file
- **WHEN** the user triggers the "New File" action and enters a chapter name
- **THEN** the system creates `<name>.md` inside `content/` and selects it as the active file in the editor.
