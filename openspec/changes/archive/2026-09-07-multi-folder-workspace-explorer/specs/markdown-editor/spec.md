## MODIFIED Requirements

### Requirement: Instant Rendering WYSIWYG Editor
The central editing area SHALL render markdown, mermaid diagrams, and plain text using Vditor in Instant Rendering mode, displaying formatted headers, tables, code blocks, mermaid graphs, and images inline for any active file from `content/` or `resources/`.

#### Scenario: Switching active markdown chapter
- **WHEN** the user selects a file from either the Content or Resources sidebar section
- **THEN** Vditor loads the file content and renders formatted markdown and code blocks inline with autosave bound to that specific file.

#### Scenario: Editing Mermaid diagram source
- **WHEN** the user opens a `.mmd` or markdown file containing mermaid code blocks from `resources/`
- **THEN** Vditor displays the source and renders the diagram visualization inline.

## ADDED Requirements

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
