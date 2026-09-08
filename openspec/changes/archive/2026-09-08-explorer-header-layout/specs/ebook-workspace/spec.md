## MODIFIED Requirements

### Requirement: Multi-Folder Explorer Structure and Section State Persistence
The system SHALL organize project files in the left sidebar into four distinct collapsible accordion sections: `Content`, `Resources`, `Assets`, and `Dist`, and SHALL persist the open/collapsed state of each accordion section per workspace. The system SHALL render each section's icon, section title, item count badge, and contextual action buttons inside the persistent expansion header slot so that section identity, counts, and action buttons remain visible and accessible in both expanded and collapsed states. Section header action buttons SHALL prevent event propagation so clicking them does not toggle the section's expansion state.

#### Scenario: Rendering accordion explorer with saved state
- **WHEN** an ebook workspace is opened
- **THEN** the sidebar renders four collapsible sections (`Content`, `Resources`, `Assets`, and `Dist`) restoring each section's open or collapsed state from the saved configuration, with all section headers displaying their corresponding category icon, title, item counter badge, and action buttons.

#### Scenario: Collapsing an accordion section
- **WHEN** the user collapses an accordion section in the sidebar
- **THEN** the collapsible body hides its child files while the section header remains fully visible, displaying the section's icon, title, item count badge, action button, and collapsed chevron toggle.

#### Scenario: Clicking header action button
- **WHEN** the user clicks the "New File" or "Upload Asset" button located in an accordion header
- **THEN** the corresponding creation or upload dialog opens without altering the accordion section's expanded or collapsed state.

#### Scenario: Toggling accordion section
- **WHEN** the user clicks the header (outside of action buttons) to collapse or expand an accordion section in the sidebar
- **THEN** the system immediately updates the UI and persists the new state for that workspace in configuration.

#### Scenario: Creating a new file from dialog without slot errors
- **WHEN** the user confirms file creation in the new file dialog
- **THEN** the system creates the file, notifies the user with a positive toast notification, selects the new file, and updates the file explorer without encountering parent slot deletion runtime errors.
