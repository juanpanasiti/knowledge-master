## MODIFIED Requirements

### Requirement: Flowing Scrollable Project Lists
The dashboard SHALL organize projects into two horizontal tiers: a compact Recent Projects tier with horizontal scrolling and an expansive Workspace Library tier filling all remaining vertical viewport space with vertical scrolling.

#### Scenario: Project list overflowing available viewport
- **WHEN** recent or discovered ebook projects exceed the available visible viewport area
- **THEN** the Recent Projects tier provides horizontal scrolling and the Workspace Library tier provides vertical scrolling while the dashboard header remains pinned.

#### Scenario: Recent projects horizontal scrolling
- **WHEN** the user has opened multiple recent projects that exceed the horizontal width of the viewport
- **THEN** the Recent Projects shelf displays a smooth horizontal scrollbar and allows horizontal scrolling while maintaining fixed vertical height.

#### Scenario: Workspace library vertical scrolling
- **WHEN** discovered ebook projects in the workspace library exceed the remaining vertical viewport height
- **THEN** the Workspace Library shelf expands to fill all remaining vertical viewport space and provides an independent vertical scrollbar.

## ADDED Requirements

### Requirement: Front-Facing Book Cover Cards
The system SHALL present each ebook as a physical front-facing book card with a realistic book spine crease highlight on the left edge, elevation drop shadows, hover lift animation, and clean typography for title and author beneath the cover.

#### Scenario: Rendering ebook with custom cover image
- **WHEN** an ebook project contains a valid custom cover image at `assets/cover.png`
- **THEN** the system renders the book card displaying the custom cover image with the realistic book spine overlay and elevation shadow.

#### Scenario: Rendering ebook with default or placeholder cover
- **WHEN** an ebook project does not have a custom cover image or contains the default placeholder image
- **THEN** the system generates a styled book cover with a deterministic gradient, book emblem, and styled editorial typography.

#### Scenario: Hovering over recent project card
- **WHEN** the user hovers the cursor over a recent project card
- **THEN** the card performs a subtle upward elevation animation and displays a discreet remove button (`×`) in the upper right corner to remove the book from the recent list.

#### Scenario: Clicking a book card
- **WHEN** the user clicks anywhere on an ebook card in either the recent shelf or the workspace library
- **THEN** the system immediately opens that ebook workspace in the editor.

### Requirement: Configurable Cover Size Settings
The system SHALL provide a Settings dialog accessible from the dashboard header to configure book cover card sizing (`small`, `medium`, or `large`), default to `medium`, and persist the selection in `config.json`.

#### Scenario: Changing cover size in settings
- **WHEN** the user opens the Settings dialog, selects a new cover size option, and confirms
- **THEN** the system saves the chosen `cover_size` in `config.json` via `ConfigManager` and immediately re-renders the dashboard book cards with the chosen dimensions.

#### Scenario: Preserving cover size across restarts
- **WHEN** the application is restarted after setting cover size to `small` or `large`
- **THEN** the system loads the saved `cover_size` from `config.json` and renders the dashboard cards with the saved size.
