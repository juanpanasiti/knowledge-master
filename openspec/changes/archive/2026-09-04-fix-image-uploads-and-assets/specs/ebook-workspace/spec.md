## ADDED Requirements

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
