# Design: Dashboard Horizontal Bookshelf and Cover Size Settings

## Context

Knowledge Master is a desktop application built with NiceGUI running inside PyWebView on Linux. The entry dashboard currently shows two vertical columns for Recent Projects and Workspace Library, causing poor space utilization and lacking visual cover previews. Ebook workspaces contain metadata (`metadata.json`) and an `assets/` directory where `cover.png` may reside (either as a user-provided image or as the default 68-byte 1x1 PNG).

## Goals / Non-Goals

**Goals:**
- Implement a two-tier horizontal dashboard layout:
  - Row 1: Recent Projects shelf with horizontal scrolling (`overflow-x-auto`).
  - Row 2: Complete Workspace Library filling remaining vertical space (`flex-1 min-h-0`) with a responsive grid and vertical scrolling (`overflow-y-auto`).
- Render realistic front-facing book cover cards with ~1:1.45 aspect ratio, book spine binding highlights, elevation drop shadows, hover lift animations, and clean typography below the cover.
- Support both custom cover images (from `assets/cover.png`) and elegantly generated fallback covers with title-derived deterministic color gradients.
- Show an overlay remove button (`×`) on hover for recent projects.
- Add a Settings modal dialog accessible via a gear button in the dashboard header to configure cover sizing (`small`, `medium` [default], `large`), persisted in `config.json`.

**Non-Goals:**
- Multi-tab preferences window (settings is kept as a focused modal dialog).
- Editing or generating new cover image files during dashboard rendering (read-only presentation).

## Decisions

### 1. Two-Tier Horizontal Layout Structure
- **Decision**: Structure `DashboardView` container as a vertical flex column:
  - Header: Fixed height with title, branding, and action buttons (`Settings`, `Open Folder`, `New Ebook`).
  - Shelf 1 (Recent Projects): Fixed height (determined by selected cover size + typography height, e.g. ~270px for medium), horizontal flex row with `overflow-x-auto flex-nowrap gap-5`.
  - Shelf 2 (Workspace Library): Flexible height (`flex-1 min-h-0 flex flex-col`), heading row, and an internal scrolling container with `overflow-y-auto` containing a responsive CSS grid (`grid grid-cols-[repeat(auto-fill,minmax(var(--card-w),1fr))] gap-6 pb-8`).
- **Rationale**: This maximizes screen real estate usage, eliminating large empty zones at the bottom of the window while giving prominence to recently opened work.

### 2. Front-Facing Book Cover Card Component
- **Decision**: Create a dedicated rendering helper `_render_book_card(ws, on_click, on_remove=None, size_config=...)` that produces:
  - An outer card wrapper with fixed width corresponding to the active cover size setting.
  - A cover container with ratio ~1:1.45 (`rounded-r-md rounded-l-xs overflow-hidden relative shadow-lg hover:shadow-2xl hover:-translate-y-1.5 transition-all duration-200 cursor-pointer`).
  - Left-edge book spine effect: An absolute positioned overlay (`w-3 h-full left-0 top-0 pointer-events-none bg-gradient-to-r from-white/10 via-black/25 to-transparent border-r border-white/5`).
  - Cover image handling:
    - If `assets/cover.png` exists and is larger than 100 bytes (distinguishing custom covers from the 68-byte default placeholder), read and embed as a base64 PNG data URI (`data:image/png;base64,...`) or serve directly via NiceGUI. Base64 embedding eliminates multi-workspace asset routing complexity.
    - If placeholder or missing: render a styled editorial book cover with a deterministic gradient (selected by hashing the title across a curated palette of rich, dark gradients: indigo/slate, slate/emerald, midnight/cyan, amber/crimson) with an open book icon emblem and styled typography.
  - Hover removal action: For recent items, render an absolute positioned `×` button in the top-right corner with `opacity-0 group-hover:opacity-100 transition-opacity` to keep the resting cover pristine.
  - Metadata text below: Book title in bold legible text (truncated with tooltip on overflow) and author name in muted gray text.

### 3. Configurable Cover Size Settings in Core & UI
- **Decision**:
  - Add `cover_size: str = Field(default="medium")` to `AppSettings` in `src/ebook_editor/core/models.py`.
  - Add `set_cover_size(size: str)` to `ConfigManager` in `src/ebook_editor/core/config.py`.
  - Define three size presets in `dashboard.py`:
    - `small`: Width 120px, Cover Height 174px.
    - `medium`: Width 150px, Cover Height 218px (Default).
    - `large`: Width 185px, Cover Height 268px.
  - In `dashboard.py`, add a gear icon button in the top action bar:
    - Clicking opens `ui.dialog` with title "Settings" and a cover size selector (radio buttons or toggle).
    - On selection change, persist through `state.config_manager.set_cover_size(val)` and call `self.render()` to immediately reflect the new layout.

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────┐
│ AppSettings (config.json)                              │
│ cover_size: "small" | "medium" | "large"               │
└─────────────────────────┬──────────────────────────────┘
                          │ loaded by
                          ▼
┌────────────────────────────────────────────────────────┐
│ ConfigManager / AppState                               │
└─────────────────────────┬──────────────────────────────┘
                          │ passed to
                          ▼
┌────────────────────────────────────────────────────────┐
│ DashboardView                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Header: [Settings (Gear)] [Open Folder] [New Ebook]│ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Row 1: Recent Projects (Horizontal Scroll)         │ │
│ │   [Book Card (Cover + Spine + Title + Hover [x])]  │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Row 2: Workspace Library (Full-Height Vert Scroll) │ │
│ │   [Book Card Grid (Responsive Auto-Fill)]          │ │
│ └────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **Base64 Cover Image Overhead**: Encoding large cover images as base64 strings in memory during dashboard rendering could add minor overhead if dozens of multi-megabyte images exist.
  - *Mitigation*: Ebook covers are typically lightweight; we can also limit thumbnail dimensions or decode cleanly. The existing user library typically contains a modest number of books in `~/knowledge-master/ebooks/`.
- **Horizontal Scroll Usability with Trackpads/Mice**: Standard mouse wheels scroll vertically by default.
  - *Mitigation*: We ensure standard web `overflow-x-auto` styles are cleanly visible, and users can use shift+wheel, touch/trackpad drag, or the styled horizontal scrollbar.
