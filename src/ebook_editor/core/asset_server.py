"""Asset routes and media upload handlers for active workspace."""

import re
from pathlib import Path
from typing import Callable
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from ebook_editor.core.workspace import EbookWorkspace

STATIC_VDITOR_DIR = (
    Path(__file__).parent.parent / "static" / "vendor" / "vditor"
).resolve()


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded asset filename, removing dangerous characters."""
    clean = re.sub(r"[^\w\.\-\_]", "_", filename.strip())
    return clean or "asset_upload.png"


def register_asset_routes(
    app: FastAPI,
    get_active_workspace: Callable[[], EbookWorkspace | None],
) -> None:
    """Register workspace asset endpoints and static mounts onto the FastAPI app."""

    # Register Vditor static bundle if directory exists
    if STATIC_VDITOR_DIR.is_dir():
        from nicegui import app as nicegui_app
        nicegui_app.add_static_files("/static/vendor/vditor", str(STATIC_VDITOR_DIR))
        nicegui_app.add_static_files("/static/vendor/vditor/dist", str(STATIC_VDITOR_DIR))

    @app.get("/api/workspace/assets/{file_path:path}")
    async def serve_workspace_asset(file_path: str):
        """Serve a static asset from the active ebook project's assets directory."""
        workspace = get_active_workspace()
        if not workspace:
            raise HTTPException(status_code=404, detail="No active ebook workspace.")

        base_assets_dir = workspace.assets_dir.resolve()
        requested_file = (base_assets_dir / file_path).resolve()

        # Path traversal guard
        try:
            requested_file.relative_to(base_assets_dir)
        except ValueError:
            raise HTTPException(status_code=403, detail="Access outside assets directory forbidden.")

        if not requested_file.is_file():
            raise HTTPException(status_code=404, detail=f"Asset '{file_path}' not found.")

        return FileResponse(requested_file)

    @app.post("/api/workspace/upload-asset")
    async def upload_workspace_asset(file: UploadFile = File(...)):
        """Upload an image into the active ebook assets directory."""
        workspace = get_active_workspace()
        if not workspace:
            raise HTTPException(status_code=400, detail="No active ebook workspace.")

        workspace.ensure_structure()
        original_name = file.filename or "upload.png"
        safe_name = sanitize_filename(original_name)

        # Avoid collision
        dest = workspace.assets_dir / safe_name
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while dest.exists():
            dest = workspace.assets_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        contents = await file.read()
        dest.write_bytes(contents)

        url = f"/api/workspace/assets/{dest.name}"
        relative_path = f"./assets/{dest.name}"

        return JSONResponse(
            {
                "filename": dest.name,
                "url": url,
                "relative_path": relative_path,
                "code": 0,
                "msg": "",
                "data": {
                    "errFiles": [],
                    "succMap": {
                        original_name: url,
                    },
                },
            }
        )
