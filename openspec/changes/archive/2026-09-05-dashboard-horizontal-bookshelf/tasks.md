## 1. Core Models and Configuration Updates

- [x] 1.1 Add `cover_size: str = "medium"` to `AppSettings` in `src/ebook_editor/core/models.py` and `set_cover_size(size: str)` to `ConfigManager` in `src/ebook_editor/core/config.py`. Verify with `uv run pytest`.
- [x] 1.2 Add automated unit tests covering `cover_size` default values, mutation, and persistence in `tests/test_config.py`. Verify by running `uv run pytest tests/test_config.py`.

## 2. Book Cover Card Component & Rendering Logic

- [x] 2.1 Implement front-facing book cover card renderer in `src/ebook_editor/ui/dashboard.py` supporting custom cover images, generated fallback gradient covers with book emblem, left-edge spine crease overlay, elevation drop shadows, and title/author metadata beneath the cover. Verify by running `uv run pytest`.
- [x] 2.2 Implement hover-revealed remove button (`×`) on recent book cards to remove items from the recent projects list. Verify with manual UI interaction.

## 3. Two-Tier Horizontal Dashboard Layout

- [x] 3.1 Refactor Recent Projects in `src/ebook_editor/ui/dashboard.py` into a compact horizontal shelf with `overflow-x-auto`, smooth scrolling, and an empty state card. Verify horizontal scrolling behavior.
- [x] 3.2 Refactor Workspace Library in `src/ebook_editor/ui/dashboard.py` into a full-height container (`flex-1 min-h-0`) with responsive grid layout and independent vertical scrolling (`overflow-y-auto`). Verify it occupies all remaining vertical space.

## 4. Settings Dialog & Cover Sizing Wiring

- [x] 4.1 Add Settings button (`settings` icon) to the dashboard header and implement the Settings modal dialog with radio or button toggle options for `Small`, `Medium`, and `Large`. Verify that selection persists in `config.json`.
- [x] 4.2 Connect active `cover_size` to card dimensions and trigger instant dashboard re-rendering upon selection change. Verify responsiveness and visual consistency across small, medium, and large sizes.

## 5. Versioning, Documentation, and Final Validation

- [x] 5.1 Bump project version in `pyproject.toml` from `0.1.3` to `0.2.0` and update `README.md` to document the bookshelf layout and cover size preferences. Verify package build metadata with `uv lock`.
- [x] 5.2 Run complete automated test suite (`uv run pytest`) and execute final manual validation to ensure all requirements and scenarios in the proposal and delta specs are satisfied.
