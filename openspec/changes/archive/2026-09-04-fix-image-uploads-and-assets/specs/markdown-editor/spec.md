## MODIFIED Requirements

### Requirement: Media Asset Insertion and Resolution
The system SHALL support inserting images via drag & drop, clipboard paste (`Ctrl+V`), manual file dialog, and the Vditor toolbar upload action, saving the image into the ebook's `assets/` directory, and SHALL immediately render the image inline using `vditor.insertMD()` without leaving unparsed markdown text.

#### Scenario: Pasting an image from clipboard
- **WHEN** the user pastes an image from the clipboard into Vditor
- **THEN** the system writes the image file into the active ebook's `assets/` folder and inserts `![image](./assets/<filename>)` into the editor.

#### Scenario: Uploading image via editor toolbar
- **WHEN** the user uploads an image using the Vditor toolbar upload action
- **THEN** the system saves the asset, invokes `vditor.insertMD()`, compiles the markdown into an image node via Lute, and renders the image preview inline immediately.
