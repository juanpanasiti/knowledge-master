## Context

NiceGUI 3 introduced breaking changes to `UploadEventArguments` by migrating from a synchronous byte stream property (`event.content`) to an asynchronous `FileUpload` instance (`event.file: SmallFileUpload | LargeFileUpload`), where reading the content requires `await event.file.read()`. Prior upload callbacks synchronously accessed `.content`, resulting in uncaught `AttributeError` exceptions and leaving dialogs stuck in an unfinished state.

Furthermore, markdown rendering engines inside the editor and previews generate standard relative URLs such as `assets/foo.png` or `./assets/foo.png`. When loaded inside an HTTP browser session or webview, these translate into GET requests to `/assets/foo.png` or `/content/assets/foo.png`. Previously, only the canonical API route `/api/workspace/assets/{path}` was exposed by the asset server, causing 404 responses.

Finally, Vditor's default upload callback in `ir` (Instant Rendering) mode inserted plain text syntax rather than instructing Lute to parse and inject an active markdown AST node.

See `proposal.md` for background and user impact.

## Goals / Non-Goals

**Goals:**
- Provide asynchronous upload handling compatible with NiceGUI 3's `FileUpload` across all upload entry points (`MetadataPanelComponent` and `WorkspaceView`).
- Guarantee clean dialog lifecycle management using `try...finally: dialog.close()`, preventing frozen upload dialog states even if unexpected errors occur.
- Expose relative route aliases in `asset_server.py` (`/assets/{file_path:path}` and `/content/assets/{file_path:path}`) mapping directly to the active workspace's `assets/` directory.
- Ensure Vditor invokes `vditor.insertMD()` on upload success to trigger Lute's instant markdown node compilation and immediate visual rendering.
- Maintain test coverage for both relative asset routing and upload file handling.

**Non-Goals:**
- Refactoring the entire asset management system to cloud/external object storage (all assets remain local disk files in the ebook's `assets/` directory).
- Replacing Vditor with a different markdown editing engine.
- Modifying image format conversion or client-side resizing during upload.

## Decisions

### 1. Asynchronous Upload Processing with Defensive Fallback
- **Decision**: Declare all `on_upload` event handlers as `async def`, extracting file content via `await event.file.read()` if `hasattr(event, "file")` exists, with a fallback to `event.content.read()` or `event.content` for backward compatibility.
- **Rationale**: NiceGUI 3's `UploadEventArguments` uses Starlette/FastAPI's async file upload mechanics under the hood. Handling this asynchronously aligns with NiceGUI 3 architecture and prevents blocking the server event loop during large asset transfers.
- **Alternatives Considered**:
  - *Keep handlers synchronous and run `asyncio.run(event.file.read())`*: Unsafe inside an active FastAPI/NiceGUI event loop; raises `RuntimeError: This event loop is already running`.
  - *Patch NiceGUI's UploadEventArguments globally*: Fragile monkey-patching that breaks across NiceGUI micro-updates.

### 2. Guaranteed Dialog Closure in `finally` Blocks
- **Decision**: Wrap file extraction, persistence, and notification logic in a `try...finally` block that unconditionally calls `dialog.close()`.
- **Rationale**: If file reading or directory writing fails (or if `ui.notify` fails due to slot context absence during automated tests), the upload dialog would otherwise remain permanently visible on top of the workspace.
- **Alternatives Considered**:
  - *Only call `dialog.close()` at the end of the `try` block*: Leaves the dialog open in an error/frozen state whenever an exception is raised.

### 3. FastAPI Route Aliasing for Relative Asset Resolution
- **Decision**: In `src/ebook_editor/core/asset_server.py`, mount explicit GET endpoints for `/assets/{file_path:path}` and `/content/assets/{file_path:path}` that delegate to the active workspace `assets_dir` resolver.
- **Rationale**: Web browsers and `pywebview` resolve relative image URLs (`./assets/img.png`) against the base document path (`/` or `/content`), issuing HTTP GET requests to `/assets/...` or `/content/assets/...`. Adding these route handlers directly allows standard markdown relative paths to work without requiring complex markdown URL preprocessing before editor loading.
- **Alternatives Considered**:
  - *Rewrite all markdown image URLs on chapter load to use absolute `/api/workspace/assets/...` paths*: Pollutes the clean markdown files on disk and makes them less portable if opened in external editors like Obsidian or Typora.

### 4. Immediate Rendering via `vditor.insertMD()`
- **Decision**: Configure `upload.success` in `src/ebook_editor/ui/components/editor.py` to trigger `vditor.insertMD()` with the markdown image string.
- **Rationale**: In Vditor's Instant Rendering mode, `insertValue()` or default pasting may insert raw markdown text that requires a manual keystroke or blur event to trigger Lute AST re-compilation into an `<img>` element. Calling `insertMD()` forces Lute to immediately evaluate the node and display the rendered image.
- **Alternatives Considered**:
  - *Rely on default Vditor upload handling*: Leaves plain text `![image](...)` in the editor until the user interacts with the surrounding paragraph.

## Risks / Trade-offs

- **[Risk: Multiple open workspaces or switching projects]** → Asset routes serve files from the currently active workspace (`state.workspace.assets_dir`). If a project is closed or switched, previously cached relative URLs might point to old assets.
  - *Mitigation*: Asset server endpoints validate that `state.workspace` is loaded and that the requested file exists within the project boundaries before returning a 200 response, returning 404 otherwise.
- **[Risk: `ui.notify` failing in non-client context during tests]** → In NiceGUI, invoking `ui.notify` outside a slot context raises a `RuntimeError`.
  - *Mitigation*: Wrap `ui.notify` calls in a safe exception handler or check context so automated headless tests run cleanly without mocking NiceGUI internal slot stacks.
