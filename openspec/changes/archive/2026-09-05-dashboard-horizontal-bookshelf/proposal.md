# Proposal: Dashboard Horizontal Bookshelf and Cover Size Settings

## Why

The current dashboard displays Recent Projects and the Workspace Library in two narrow vertical columns side-by-side. This layout leaves extensive unused vertical space at the bottom of the window, truncates book paths and titles, and does not provide an intuitive visual representation of books. Furthermore, users cannot visually inspect their book covers or customize display dimensions.

Transitioning to a two-tier horizontal bookshelf layout—featuring a horizontal-scrolling recent books shelf and an expansive vertical-scrolling library grid with realistic front-facing book covers and customizable sizing—dramatically improves readability, visual appeal, and spatial efficiency.

## What Changes

- **Horizontal Two-Tier Dashboard Layout**: Replace the two-column layout in `DashboardView` with two stacked horizontal tiers:
  - **Tier 1 (Top)**: Compact Recent Projects shelf with horizontal scrolling (`overflow-x-auto`).
  - **Tier 2 (Bottom)**: Workspace Library shelf filling all remaining vertical viewport space (`flex-1 min-h-0`) with a responsive grid and vertical scrolling (`overflow-y-auto`).
- **Realistic Front-Facing Book Cover Cards**:
  - Render books as physical front-facing volumes (proportions ~1:1.45) with book spine crease highlights and realistic elevation drop shadows.
  - Display actual cover images if custom `assets/cover.png` exists; fallback to an elegant generated cover with editorial typography and deterministic modern gradients when using default placeholders.
  - Place book title and author cleanly beneath each book cover with full readability and tooltip support on truncation.
  - Include an overlay `×` removal button on recent book covers that reveals smoothly on mouse hover.
  - Interactive hover state: subtle upward lift (`-translate-y-2`) and enhanced shadow depth.
- **Dashboard Settings Dialog & Cover Sizing Configuration**:
  - Add a Settings button (gear icon) to the dashboard header bar.
  - Provide a Settings modal dialog allowing users to choose cover dimensions (`small`, `medium` [default], `large`).
  - Persist `cover_size` in `AppSettings` (`config.json`) via `ConfigManager` and update the view dynamically.

### Goals
- Present recent and discovered ebooks as visual front-facing books.
- Optimize window space utilization by dedicating all remaining vertical height to the complete workspace library.
- Allow users to configure cover card sizes with instant persistence across restarts.
- Maintain seamless one-click opening of any ebook into the editor workspace.

### Non-Goals
- Adding multi-page settings navigation (settings remains a lightweight modal dialog for now).
- Changing the chapter file tree or internal editor layout within `WorkspaceView`.
- Introducing external cover fetching from remote web APIs.

## Capabilities

### Modified Capabilities
- `ebook-workspace`: Modify dashboard layout requirements to replace the two-column layout with a two-tier horizontal shelf architecture (horizontal scroll for recents, full-height vertical grid scroll for library), specify front-facing book cover styling with hover interactions, and add cover size settings configuration in `AppSettings`.

## Impact

- **UI Layer (`src/ebook_editor/ui/dashboard.py`)**: Major overhaul of the dashboard render tree, introducing realistic book card components, horizontal scrolling container, vertical grid container, and settings modal dialog.
- **Core Models & Config (`src/ebook_editor/core/models.py`, `config.py`)**: Add `cover_size: str = "medium"` field to `AppSettings` schema and corresponding helper `set_cover_size(size: str)` in `ConfigManager`.
- **SemVer Impact**: Minor version bump (`0.1.3` -> `0.2.0` in `pyproject.toml`) due to new UI features and configuration settings.
