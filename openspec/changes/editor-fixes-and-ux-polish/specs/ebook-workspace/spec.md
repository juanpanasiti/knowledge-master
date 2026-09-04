## MODIFIED Requirements

### Requirement: Metadata Schema Validation
The system SHALL validate and persist project metadata in `metadata.json` including title, author, description, cover image relative path, tags, creation timestamp, and update timestamp, and SHALL tolerate `null` values for optional text fields such as description without crashing.

#### Scenario: Loading metadata with null description
- **WHEN** the application opens an existing ebook project whose `metadata.json` has `"description": null`
- **THEN** the system successfully parses the metadata, defaulting description to an empty string without raising validation errors.

#### Scenario: Updating project metadata
- **WHEN** the user edits the metadata fields in the metadata panel and saves
- **THEN** the system updates `metadata.json` ensuring all fields comply with the schema and sets `updated_at` to the current UTC timestamp.

## ADDED Requirements

### Requirement: Workspace and Dashboard Action Tooltips
All icon-only action buttons across the workspace navigation header, file tree explorer, Git version control panel, and dashboard SHALL provide descriptive tooltips.

#### Scenario: Hovering over icon-only buttons
- **WHEN** the user hovers over the chapter options button (`more_vert`), the unstage button (`remove`), or the remove recent button (`close`)
- **THEN** the application displays a descriptive tooltip clarifying the button's action.
