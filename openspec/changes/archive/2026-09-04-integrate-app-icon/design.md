## Context

See `proposal.md` for motivation. Currently, `assets/icon.png` resides in the project root. When Knowledge Master is packaged as a wheel via Hatchling, only `src/ebook_editor` is bundled into the distribution. Furthermore, `src/ebook_editor/main.py` invokes NiceGUI's `ui.run()` without the `favicon` argument, defaulting to NiceGUI's stock branding during runtime.

## Goals / Non-Goals

**Goals:**
- Package the icon asset inside `src/ebook_editor/static/` so it is distributed with the Python package.
- Supply the icon path as `favicon` in `ui.run()` so the runtime browser tab and PyWebView window display the custom icon.
- Maintain desktop launcher icon synchronization in `install.sh`.
- Increment project version in `pyproject.toml` to `0.1.3`.

**Non-Goals:**
- Creating dynamic multi-resolution icon generators at runtime.
- Supporting custom user-uploaded app icons from preferences.

## Decisions

### 1. Bundle icon as static package asset
- **Choice**: Copy `assets/icon.png` to `src/ebook_editor/static/favicon.png`.
- **Rationale**: `src/ebook_editor/static` is already bundled by Hatchling for local Vditor assets. Placing the favicon there ensures it is always present when installed via `uv tool install` or `pip`.
- **Alternatives considered**: Referencing `assets/icon.png` relative to the repository root. This fails once installed globally in `~/.local/share/uv/tools/...` because root repo assets are not packaged.

### 2. Configure `favicon` in `ui.run()`
- **Choice**: Resolve `FAVICON_PATH = Path(__file__).parent / "static" / "favicon.png"` and supply `favicon=FAVICON_PATH` to `ui.run()`.
- **Rationale**: NiceGUI supports `pathlib.Path` directly in `ui.run(favicon=...)`, serving it automatically with correct MIME types and caching headers.

### 3. System desktop installer synchronization
- **Choice**: Keep `install.sh` targeting `~/.local/share/icons/hicolor/128x128/apps/knowledge-master.png` from `assets/icon.png`.
- **Rationale**: Keeps full backward-compatibility with the existing system launcher integration.

## Risks / Trade-offs

- **[Asset Duplication]** Maintaining `assets/icon.png` and `src/ebook_editor/static/favicon.png` creates two copies of the image.
  - *Mitigation*: `assets/icon.png` serves as the high-res master asset for Linux desktop packaging, while `static/favicon.png` is the runtime web/UI asset.
