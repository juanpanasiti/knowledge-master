# Markdown Editor Specification

## Purpose

Delivers a native-window WYSIWYG markdown editing experience powered by Vditor with offline bundled assets, dark mode default, debounced autosave, and local asset rendering.

## Requirements

### Requirement: Native Desktop Window Execution
The application SHALL launch in a dedicated standalone native desktop window using pywebview without opening browser tabs or displaying browser navigation bars.

#### Scenario: Application startup
- **WHEN** the user executes the application command
- **THEN** a native desktop window opens directly with the configured initial dimensions (1280x800) and window title.

### Requirement: Instant Rendering WYSIWYG Editor
The central editing area SHALL render markdown, mermaid diagrams, and plain text using Vditor in Instant Rendering mode, displaying formatted headers, tables, code blocks, mermaid graphs, and images inline for any active file from `content/` or `resources/`.

#### Scenario: Switching active markdown chapter
- **WHEN** the user selects a file from either the Content or Resources sidebar section
- **THEN** Vditor loads the file content and renders formatted markdown and code blocks inline with autosave bound to that specific file.

#### Scenario: Editing Mermaid diagram source
- **WHEN** the user opens a `.mmd` or markdown file containing mermaid code blocks from `resources/`
- **THEN** Vditor displays the source and renders the diagram visualization inline.

### Requirement: Asset Preview and Markdown Link Modal
The system SHALL provide an interactive preview dialog when an image asset is clicked in the Assets accordion section, displaying the full-resolution preview, file information, and a button to copy the Markdown reference string (`![name](assets/filename)`) to the clipboard.

#### Scenario: Opening asset preview
- **WHEN** the user clicks an image asset in the Assets sidebar section
- **THEN** a modal dialog opens displaying the image preview, filename, and a "Copy Markdown Link" action button.

#### Scenario: Copying markdown link
- **WHEN** the user clicks "Copy Markdown Link" inside the asset preview modal
- **THEN** the system copies `![<name>](assets/<filename>)` to the user's clipboard and displays a confirmation notification.

### Requirement: Dist Build Output Interaction
The system SHALL provide interactive actions for exported build deliverables in the `dist/` sidebar section, allowing users to view PDF files in a browser tab and download or reveal EPUB files.

#### Scenario: Viewing generated PDF
- **WHEN** the user clicks a `.pdf` file in the Dist sidebar section
- **THEN** the application opens the PDF in a browser tab via a dedicated dist endpoint, rendering the document in the browser's built-in PDF viewer.

#### Scenario: Downloading or opening generated EPUB
- **WHEN** the user clicks a `.epub` file in the Dist sidebar section
- **THEN** the application triggers the download of the EPUB file with proper MIME type headers.

### Requirement: Debounced Autosave
The system SHALL automatically persist editor changes to the active markdown file after a period of typing inactivity and display save status.

#### Scenario: Typing with autosave triggered
- **WHEN** the user modifies text in the editor and stops typing for 500 milliseconds
- **THEN** the system saves the file content to disk and updates the status indicator from "Saving..." to "Saved".

### Requirement: Theme Selector with Dark Default
The editor and user interface SHALL default to a dark theme and SHALL provide an interactive toggle to switch between dark and light themes.

#### Scenario: Toggling UI theme
- **WHEN** the user switches the theme toggle
- **THEN** both the NiceGUI shell and the Vditor editor synchronously switch between dark and light color palettes.

### Requirement: Media Asset Insertion and Resolution
The system SHALL support inserting images via drag & drop, clipboard paste (`Ctrl+V`), manual file dialog, and the Vditor toolbar upload action, saving the image into the ebook's `assets/` directory, and SHALL immediately render the image inline using `vditor.insertMD()` without leaving unparsed markdown text.

#### Scenario: Pasting an image from clipboard
- **WHEN** the user pastes an image from the clipboard into Vditor
- **THEN** the system writes the image file into the active ebook's `assets/` folder and inserts `![image](./assets/<filename>)` into the editor.

#### Scenario: Uploading image via editor toolbar
- **WHEN** the user uploads an image using the Vditor toolbar upload action
- **THEN** the system saves the asset, invokes `vditor.insertMD()`, compiles the markdown into an image node via Lute, and renders the image preview inline immediately.

### Requirement: Local Dynamic Asset Serving
The system SHALL serve images stored in the active ebook's `assets/` directory through a dedicated backend route ensuring relative links in markdown resolve properly.

#### Scenario: Rendering local image preview
- **WHEN** markdown containing `![alt](./assets/photo.png)` is rendered in Vditor
- **THEN** the image is fetched from the dynamic asset route pointing to the active ebook's `assets/photo.png` and rendered in the view.

### Requirement: Full Height Viewport and Editor Sheet Scrolling
The editor layout SHALL occupy 100% of the available window height without vertical collapsing or dead space, and the central markdown writing sheet SHALL span to the bottom window boundary and handle vertical scrolling independently while preserving a fixed top toolbar.

#### Scenario: Long document vertical scrolling
- **WHEN** the active markdown document contains more content than fits in the visible viewport
- **THEN** a vertical scrollbar appears specifically for the writing sheet, allowing the user to scroll through the document while the editor toolbar and subheader remain pinned.

### Requirement: Editor Reading Width Toggle
The editor interface SHALL provide an interactive width toggle allowing users to switch between a centered readable width and full-width layout.

#### Scenario: Toggling to centered reading width
- **WHEN** the user activates the width toggle to centered mode
- **THEN** the editor writing sheet centers horizontally within the middle column with a maximum readable width constraint.

#### Scenario: Toggling to full width
- **WHEN** the user activates the width toggle to full-width mode
- **THEN** the editor writing sheet expands to occupy the complete horizontal width of the middle column.

### Requirement: Crash-Resilient Chapter Switching
The sidebar file tree and editor integration SHALL switch active chapters seamlessly without invalidating active UI component slots or throwing runtime parent deletion errors.

#### Scenario: Selecting a different chapter in the sidebar
- **WHEN** the user clicks on a different chapter in the chapter list
- **THEN** the editor loads and displays the new chapter content without raising runtime exceptions or breaking client-server event communication.

