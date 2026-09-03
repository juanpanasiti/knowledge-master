## ADDED Requirements

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
