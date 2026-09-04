## MODIFIED Requirements

### Requirement: Debounced Autosave
The system SHALL automatically persist editor changes to the active markdown file after a period of typing inactivity, extract the complete content payload from editor events, update file contents on disk, and update the save status indicator and live word count.

#### Scenario: Typing with autosave triggered
- **WHEN** the user modifies text in the editor and stops typing for 500 milliseconds
- **THEN** the system extracts the editor content payload, writes the content to the active chapter file on disk, updates the word count label to match the written words, and updates the status indicator from "Saving..." to "Saved".

## ADDED Requirements

### Requirement: List Formatting and Outdent Navigation
The editor SHALL render ordered lists with visible decimal numbering and SHALL allow users to outdent nested list items and break out into root-level normal paragraphs using toolbar buttons or standard keyboard actions.

#### Scenario: Rendering ordered list numbers
- **WHEN** the user creates an ordered list using `1. item 1` and `2. item 2`
- **THEN** the items render with clear, visible sequential decimal numbers rather than hidden counters.

#### Scenario: Outdenting and escaping nested lists via keyboard
- **WHEN** the cursor is on an empty item or paragraph within a nested list and the user presses Enter or Shift+Tab or Backspace at column zero
- **THEN** the editor decreases the indentation level by one, eventually placing the cursor on a normal paragraph at the root margin of the document.

### Requirement: Dark Mode Element Contrast and Legibility
The editor SHALL render markdown tables and block elements in dark theme using dark-slate cell backgrounds, legible text colors, and subtle borders without blinding white fills.

#### Scenario: Rendering tables in dark theme
- **WHEN** a markdown table is displayed in the active editor while dark theme is active
- **THEN** table header cells render with elevated dark slate backgrounds and light text, and table rows render with dark backgrounds and contrasting text.

### Requirement: Editor Toolbar Tooltip Visibility
The editor toolbar SHALL display informative tooltips for all formatting actions, oriented downwards to prevent clipping against container boundaries.

#### Scenario: Hovering over toolbar buttons
- **WHEN** the user hovers the cursor over any toolbar button (such as Bold, Table, Headings, or Outdent)
- **THEN** a tooltip appears below the button displaying the action name and associated keyboard shortcut.
