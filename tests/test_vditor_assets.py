"""Test existence and integrity of bundled Vditor offline assets."""

from pathlib import Path


def test_vditor_bundled_assets_exist() -> None:
    static_dir = Path(__file__).parent.parent / "src" / "ebook_editor" / "static" / "vendor" / "vditor"
    assert static_dir.is_dir(), f"Vditor directory missing at {static_dir}"

    index_js = static_dir / "index.min.js"
    assert index_js.is_file(), "index.min.js missing"
    assert index_js.stat().st_size > 100_000, "index.min.js seems truncated"

    index_css = static_dir / "index.css"
    assert index_css.is_file(), "index.css missing"
    assert index_css.stat().st_size > 10_000, "index.css seems truncated"

    js_dir = static_dir / "js"
    assert js_dir.is_dir(), "Vditor js directory missing"


def test_vditor_dist_route_serving() -> None:
    """Verify that /static/vendor/vditor/dist routes serve assets successfully with HTTP 200."""
    from fastapi import FastAPI
    from starlette.testclient import TestClient
    from ebook_editor.core.asset_server import register_asset_routes

    test_app = FastAPI()
    register_asset_routes(test_app, lambda: None)
    client = TestClient(test_app)

    # Test direct file
    r1 = client.get("/static/vendor/vditor/dist/js/i18n/en_US.js")
    assert r1.status_code == 200
    assert "VditorI18n" in r1.text

