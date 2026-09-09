## ADDED Requirements

### Requirement: Recent Projects Validation and Filtering
The Recent Projects shelf SHALL only display valid ebook workspaces that currently exist on disk and contain a valid `metadata.json` file. The system SHALL ignore or prune any entries in `recent_ebooks` that point to non-existent directories or directories that fail workspace validation (`is_valid()`).

#### Scenario: Recent list contains non-existent or invalid directory
- **WHEN** an entry in `recent_ebooks` points to a path that does not exist or lacks a valid `metadata.json`
- **THEN** the system does not render a book card for that path in the Recent Projects shelf.

#### Scenario: Recent list contains valid ebook workspace
- **WHEN** an entry in `recent_ebooks` points to an existing directory containing a valid `metadata.json`
- **THEN** the system renders a book card with its title, author, and cover.

#### Scenario: Automatic pruning of invalid recent entries
- **WHEN** the dashboard loads recent ebooks or settings are saved
- **THEN** the system removes non-existent or invalid ebook paths from the persistent recent list.
