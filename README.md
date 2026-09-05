# Knowledge Master

A native desktop markdown ebook editor and workspace manager built with Python and NiceGUI.

## Features

- **Instant Rendering Markdown Editor**: Powered by Vditor in IR (live preview) mode with bundled local assets.
- **Reliable Debounced Autosave**: Automatic persistence to disk after typing inactivity with real-time word counting and save status indication.
- **Refined Dark Mode Aesthetics**: Elevated contrast for tables, zebra striping, headers, and full visibility of ordered list numbers.
- **Fluid List Editing & Navigation**:
  - Outdent (`Shift+Tab`) and Indent (`Tab`) toolbar actions.
  - Automatic unindentation when pressing `Enter` or `Backspace` on empty nested list items to easily escape back to normal root paragraphs.
- **Two-Tier Horizontal Bookshelf**:
  - Horizontal scrolling shelf for Recent Projects with sleek card lift animations and hover-revealed removal (`×`).
  - Full-height, vertical scrolling grid for the Workspace Library occupying all remaining vertical space.
  - Realistic front-facing book covers featuring spine crease highlights, elevation drop shadows, custom cover support, and elegant fallback gradient covers.
- **Configurable Cover Sizing**: Settings dialog accessible from the dashboard header with `Small`, `Medium` (default), and `Large` cover presets persisted across sessions.
- **Local Asset Management & Media Insertion**: Drag & drop, clipboard paste, or file upload for chapter images and ebook covers, automatically resolved through relative paths and rendered instantly in the editor.
- **Local Ebook Workspaces**: Standardized ebook structure (`metadata.json`, `assets/`, `content/`) with natural chapter numbering (`1 - Title.md`, `1.1 - Section.md`).
- **Integrated Version Control**: Built-in Git staging, unstaging, commit creation, and commit history log.
- **Informative Tooltips**: Clear tooltips across all toolbar actions, file tree controls, Git buttons, and dashboard items.

## Getting Started

### Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/)

### Installation & Running

Run the desktop application directly:
```bash
uv run knowledge-master
```

### Running Tests

Execute the automated test suite:
```bash
uv run pytest
```

