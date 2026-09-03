"""Unit tests for workspace asset endpoints and security."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ebook_editor.core.asset_server import register_asset_routes
from ebook_editor.core.workspace import EbookWorkspace


def test_asset_endpoints_with_active_workspace(tmp_path: Path) -> None:
    app = FastAPI()
    ebook_dir = tmp_path / "my_ebook"
    ws = EbookWorkspace(ebook_dir)
    ws.ensure_structure()

    active_ws = ws

    def get_ws() -> EbookWorkspace | None:
        return active_ws

    register_asset_routes(app, get_ws)
    client = TestClient(app)

    # 1. Test serving default cover.png
    resp = client.get("/api/workspace/assets/cover.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"] in ["image/png", "application/octet-stream"]

    # 2. Test 404 for missing asset
    resp404 = client.get("/api/workspace/assets/missing.png")
    assert resp404.status_code == 404

    # 3. Test path traversal protection
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret_data")
    resp_traversal = client.get("/api/workspace/assets/../../secret.txt")
    assert resp_traversal.status_code in [403, 404]

    # 4. Test uploading asset
    upload_resp = client.post(
        "/api/workspace/upload-asset",
        files={"file": ("diagram.png", b"fake_png_data", "image/png")},
    )
    assert upload_resp.status_code == 200
    data = upload_resp.json()
    assert data["filename"].startswith("diagram")
    assert (ws.assets_dir / data["filename"]).is_file()
    assert (ws.assets_dir / data["filename"]).read_bytes() == b"fake_png_data"

    # 5. Verify the newly uploaded asset can be fetched
    fetch_resp = client.get(data["url"])
    assert fetch_resp.status_code == 200
    assert fetch_resp.content == b"fake_png_data"


def test_asset_endpoints_without_active_workspace() -> None:
    app = FastAPI()

    def get_ws() -> EbookWorkspace | None:
        return None

    register_asset_routes(app, get_ws)
    client = TestClient(app)

    resp = client.get("/api/workspace/assets/cover.png")
    assert resp.status_code == 404

    upload_resp = client.post(
        "/api/workspace/upload-asset",
        files={"file": ("diagram.png", b"data", "image/png")},
    )
    assert upload_resp.status_code == 400
