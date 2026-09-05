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

### Requirement: Full Height Dashboard Layout
The dashboard layout SHALL occupy 100% of the available window height without vertical collapsing or empty lower bar space.

#### Scenario: Dashboard initial rendering
- **WHEN** the user opens the application to the dashboard view
- **THEN** the dashboard container stretches vertically to fill the entire window height down to the bottom boundary.

### Requirement: Flowing Scrollable Project Lists
The dashboard SHALL organize projects into two horizontal tiers: a compact Recent Projects tier with horizontal scrolling and an expansive Workspace Library tier filling all remaining vertical viewport space with vertical scrolling.

#### Scenario: Project list overflowing available viewport
- **WHEN** recent or discovered ebook projects exceed the available visible viewport area
- **THEN** the Recent Projects tier provides horizontal scrolling and the Workspace Library tier provides vertical scrolling while the dashboard header remains pinned.

#### Scenario: Recent projects horizontal scrolling
- **WHEN** the user has opened multiple recent projects that exceed the horizontal width of the viewport
- **THEN** the Recent Projects shelf displays a smooth horizontal scrollbar and allows horizontal scrolling while maintaining fixed vertical height.

#### Scenario: Workspace library vertical scrolling
- **WHEN** discovered ebook projects in the workspace library exceed the remaining vertical viewport height
- **THEN** the Workspace Library shelf expands to fill all remaining vertical viewport space and provides an independent vertical scrollbar.

### Requirement: Front-Facing Book Cover Cards
The system SHALL present each ebook as a physical front-facing book card with a realistic book spine crease highlight on the left edge, elevation drop shadows, hover lift animation, and clean typography for title and author beneath the cover.

#### Scenario: Rendering ebook with custom cover image
- **WHEN** an ebook project contains a valid custom cover image at `assets/cover.png`
- **THEN** the system renders the book card displaying the custom cover image with the realistic book spine overlay and elevation shadow.

#### Scenario: Rendering ebook with default or placeholder cover
- **WHEN** an ebook project does not have a custom cover image or contains the default placeholder image
- **THEN** the system generates a styled book cover with a deterministic gradient, book emblem, and styled editorial typography.

#### Scenario: Hovering over recent project card
- **WHEN** the user hovers the cursor over a recent project card
- **THEN** the card performs a subtle upward elevation animation and displays a discreet remove button (`×`) in the upper right corner to remove the book from the recent list.

#### Scenario: Clicking a book card
- **WHEN** the user clicks anywhere on an ebook card in either the recent shelf or the workspace library
- **THEN** the system immediately opens that ebook workspace in the editor.

### Requirement: Configurable Cover Size Settings
The system SHALL provide a Settings dialog accessible from the dashboard header to configure book cover card sizing (`small`, `medium`, or `large`), default to `medium`, and persist the selection in `config.json`.

#### Scenario: Changing cover size in settings
- **WHEN** the user opens the Settings dialog, selects a new cover size option, and confirms
- **THEN** the system saves the chosen `cover_size` in `config.json` via `ConfigManager` and immediately re-renders the dashboard book cards with the chosen dimensions.

#### Scenario: Preserving cover size across restarts
- **WHEN** the application is restarted after setting cover size to `small` or `large`
- **THEN** the system loads the saved `cover_size` from `config.json` and renders the dashboard cards with the saved size.

### Requirement: Asynchronous Asset and Cover Upload Handling
The system SHALL accept image file uploads from NiceGUI 3 asynchronous upload events, extract file bytes using `await event.file.read()`, persist them safely to the active ebook's `assets/` directory, and guarantee that the upload modal dialog is closed upon completion or error.

#### Scenario: User changes ebook cover
- **WHEN** the user selects a valid cover image in the "Change Ebook Cover" dialog
- **THEN** the system asynchronously reads the file data, saves it to `assets/cover.png`, updates `metadata.json`, displays a success notification, refreshes the cover preview, and automatically closes the dialog.

#### Scenario: User inserts chapter image via dialog
- **WHEN** the user uploads an image file using the "Insert Image" dialog in the chapter workspace
- **THEN** the system asynchronously reads the file bytes, writes the asset into `assets/<filename>`, appends the markdown image reference into the active chapter, and closes the dialog.

### Requirement: Relative Asset Route Aliases
The backend server SHALL register `/assets/{file_path:path}` and `/content/assets/{file_path:path}` routes as aliases to the active workspace asset directory, allowing standard relative markdown paths (`./assets/...` and `assets/...`) to resolve with HTTP 200.

#### Scenario: Resolving relative markdown asset URLs
- **WHEN** an image tag in a markdown document references `./assets/photo.png` or `/assets/photo.png`
- **THEN** the backend serves the corresponding file from the active ebook's `assets/` folder with `200 OK` and the appropriate image content-type header.


