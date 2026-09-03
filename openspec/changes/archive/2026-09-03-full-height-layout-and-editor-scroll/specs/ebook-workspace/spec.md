## ADDED Requirements

### Requirement: Full Height Dashboard Layout
The dashboard layout SHALL occupy 100% of the available window height without vertical collapsing or empty lower bar space.

#### Scenario: Dashboard initial rendering
- **WHEN** the user opens the application to the dashboard view
- **THEN** the dashboard container stretches vertically to fill the entire window height down to the bottom boundary.

### Requirement: Flowing Scrollable Project Lists
The Recent Projects and Workspace Library columns on the dashboard SHALL flow vertically toward the bottom of the window with comfortable padding and provide independent vertical scrolling when project items exceed the available viewport space.

#### Scenario: Project list overflowing available viewport
- **WHEN** the number of recent or discovered ebook projects exceeds the vertical height of the column
- **THEN** that column displays an internal vertical scrollbar allowing smooth scrolling through projects while the dashboard header remains pinned.
