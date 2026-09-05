"""Ebook exporter service compiling markdown workspaces to EPUB and PDF."""

import base64
from datetime import datetime, timezone
import mimetypes
from pathlib import Path

import pypandoc
from weasyprint import CSS, HTML

from ebook_editor.core.models import EbookMetadata
from ebook_editor.core.workspace import EbookWorkspace


def get_export_assets_dir() -> Path:
    """Return the absolute path to the bundled export assets directory."""
    return Path(__file__).resolve().parent.parent.parent / "assets" / "export"


def get_epub_output_filename(metadata: EbookMetadata) -> str:
    """Construct EPUB output filename, prefixing with [DRAFT] if not finished."""
    prefix = "" if metadata.finished else "[DRAFT] "
    safe_title = metadata.title.strip() or "Untitled"
    return f"{prefix}{safe_title}.epub"


def get_pdf_output_filename(metadata: EbookMetadata) -> str:
    """Construct PDF output filename, prefixing with [DRAFT] if not finished."""
    prefix = "" if metadata.finished else "[DRAFT] "
    safe_title = metadata.title.strip() or "Untitled"
    return f"{prefix}{safe_title}.pdf"


def _build_cover_html(cover_path: Path) -> str:
    """Generate HTML snippet embedding the cover image as a base64 data URI."""
    mime_type, _ = mimetypes.guess_type(str(cover_path))
    mime_type = mime_type or "image/png"
    encoded = base64.b64encode(cover_path.read_bytes()).decode("ascii")
    data_uri = f"data:{mime_type};base64,{encoded}"

    return f"""
<div class="cover-page">
    <img class="cover-image" src="{data_uri}" alt="Cover" />
</div>
"""


def _build_cover_first_page_override_css() -> str:
    """CSS snippet removing page margins and headers/footers on the cover page."""
    return """
<style>
@page :first {
    size: A4;
    margin: 0;
    @bottom-center { content: none; }
    @bottom-left   { content: none; }
    @top-center    { content: none; }
}
</style>
"""


class EbookExporter:
    """Compiles markdown chapters from an EbookWorkspace into EPUB and PDF formats."""

    def __init__(self, assets_dir: Path | None = None) -> None:
        self.assets_dir = assets_dir or get_export_assets_dir()

    def compile_epub(self, workspace: EbookWorkspace) -> Path:
        """
        Compile workspace markdown chapters into a styled EPUB document in dist/.

        Returns the absolute path to the generated .epub file.
        """
        metadata = workspace.load_metadata()
        chapters = workspace.list_chapters()

        md_files = [str(c.path) for c in chapters]
        if not md_files:
            raise ValueError(
                f"No markdown chapter files found in '{metadata.title}'. Cannot generate EPUB."
            )

        output_dir = workspace.ensure_dist_dir()
        output_filename = get_epub_output_filename(metadata)
        output_path = output_dir / output_filename

        # Construct Pandoc arguments
        extra_args: list[str] = [
            "--from=markdown+markdown_in_html_blocks",
            "--highlight-style=tango",
            "--toc",
            "--toc-depth=2",
            f"--resource-path={workspace.root}",
        ]

        # Metadata
        extra_args.append(f"--metadata=title:{metadata.title}")
        if metadata.author:
            for author in str(metadata.author).split(","):
                clean_author = author.strip()
                if clean_author:
                    extra_args.append(f"--metadata=author:{clean_author}")

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        extra_args.append(f"--metadata=date:{date_str}")

        if metadata.description:
            extra_args.append(f"--metadata=description:{metadata.description}")

        # Cover image
        cover_path = workspace.assets_dir / "cover.png"
        if not cover_path.exists() and metadata.cover_path:
            cover_path = workspace.root / metadata.cover_path
        if cover_path.exists():
            extra_args.append(f"--epub-cover-image={str(cover_path)}")

        # Bundled styles and Lua filters
        epub_css = self.assets_dir / "epub.css"
        if epub_css.exists():
            extra_args.append(f"--css={str(epub_css)}")

        line_numbers_lua = self.assets_dir / "line-numbers.lua"
        if line_numbers_lua.exists():
            extra_args.append(f"--lua-filter={str(line_numbers_lua)}")

        callouts_lua = self.assets_dir / "obsidian-callouts.lua"
        if callouts_lua.exists():
            extra_args.append(f"--lua-filter={str(callouts_lua)}")

        syntax_alias_lua = self.assets_dir / "syntax-alias.lua"
        if syntax_alias_lua.exists():
            extra_args.append(f"--lua-filter={str(syntax_alias_lua)}")

        try:
            pypandoc.convert_file(
                source_file=md_files,
                to="epub",
                outputfile=str(output_path),
                extra_args=extra_args,
            )
        except Exception as e:
            raise RuntimeError(f"Pandoc EPUB conversion failed: {e}") from e

        return output_path

    def compile_pdf(self, workspace: EbookWorkspace) -> Path:
        """
        Compile workspace markdown chapters into an A4 PDF document in dist/.

        Pipeline: Markdown -> Pandoc (HTML5) -> WeasyPrint (PDF).
        Returns the absolute path to the generated .pdf file.
        """
        metadata = workspace.load_metadata()
        chapters = workspace.list_chapters()

        md_files = [str(c.path) for c in chapters]
        if not md_files:
            raise ValueError(
                f"No markdown chapter files found in '{metadata.title}'. Cannot generate PDF."
            )

        output_dir = workspace.ensure_dist_dir()
        output_filename = get_pdf_output_filename(metadata)
        output_path = output_dir / output_filename

        # Construct Pandoc arguments for HTML5 standalone export
        extra_args: list[str] = [
            "--from=markdown+markdown_in_html_blocks",
            "--standalone",
            "--highlight-style=tango",
            "--toc",
            "--toc-depth=2",
            f"--resource-path={workspace.root}",
            "--embed-resources",
        ]

        extra_args.append(f"--metadata=title:{metadata.title}")
        if metadata.author:
            for author in str(metadata.author).split(","):
                clean_author = author.strip()
                if clean_author:
                    extra_args.append(f"--metadata=author:{clean_author}")

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        extra_args.append(f"--metadata=date:{date_str}")

        if metadata.description:
            extra_args.append(f"--metadata=description:{metadata.description}")

        line_numbers_lua = self.assets_dir / "line-numbers.lua"
        if line_numbers_lua.exists():
            extra_args.append(f"--lua-filter={str(line_numbers_lua)}")

        callouts_lua = self.assets_dir / "obsidian-callouts.lua"
        if callouts_lua.exists():
            extra_args.append(f"--lua-filter={str(callouts_lua)}")

        syntax_alias_lua = self.assets_dir / "syntax-alias.lua"
        if syntax_alias_lua.exists():
            extra_args.append(f"--lua-filter={str(syntax_alias_lua)}")

        # Convert to HTML5
        try:
            html_content: str = pypandoc.convert_file(
                source_file=md_files,
                to="html5",
                extra_args=extra_args,
            )
        except Exception as e:
            raise RuntimeError(f"Pandoc HTML5 conversion failed: {e}") from e

        # Inject cover page if available
        cover_path = workspace.assets_dir / "cover.png"
        if not cover_path.exists() and metadata.cover_path:
            cover_path = workspace.root / metadata.cover_path

        if cover_path.exists():
            cover_html = _build_cover_html(cover_path)
            cover_css = _build_cover_first_page_override_css()
            if "<head>" in html_content:
                html_content = html_content.replace("<head>", f"<head>\n{cover_css}", 1)
            if "<body>" in html_content:
                html_content = html_content.replace("<body>", f"<body>\n{cover_html}", 1)
            else:
                html_content = cover_html + html_content

        # Load PDF stylesheets
        pdf_css = self.assets_dir / "pdf.css"
        stylesheets: list[CSS] = []
        if pdf_css.exists():
            stylesheets.append(CSS(filename=str(pdf_css)))

        # Render PDF via WeasyPrint
        try:
            doc = HTML(string=html_content, base_url=str(workspace.root))
            doc.write_pdf(target=str(output_path), stylesheets=stylesheets)
        except Exception as e:
            raise RuntimeError(f"WeasyPrint PDF rendering failed: {e}") from e

        return output_path
