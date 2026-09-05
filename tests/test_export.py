"""Unit and integration tests for ebook export and Kindle delivery."""

from pathlib import Path
from ebook_editor.core.export.credentials import (
    KindleCredentials,
    resolve_kindle_credentials,
)
from ebook_editor.core.models import AppSettings


def test_kindle_credentials_validation() -> None:
    # Incomplete credentials
    incomplete = KindleCredentials(kindle_email="test@kindle.com")
    assert not incomplete.is_configured()
    assert "smtp_user" in incomplete.missing_fields()
    assert "smtp_password" in incomplete.missing_fields()

    # Complete credentials
    complete = KindleCredentials(
        kindle_email="test@kindle.com",
        smtp_user="author@gmail.com",
        smtp_password="app-password-1234",
    )
    assert complete.is_configured()
    assert len(complete.missing_fields()) == 0


def test_resolve_credentials_waterfall(tmp_path: Path, monkeypatch) -> None:
    # 1. Clear system environment variables
    monkeypatch.delenv("KINDLE_EMAIL", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    # 2. Mock global ebook-maker env file
    global_env = tmp_path / "global_ebook_maker.env"
    global_env.write_text(
        "KINDLE_EMAIL=global@kindle.com\n"
        "SMTP_USER=global@gmail.com\n"
        "SMTP_PASSWORD=global-password\n",
        encoding="utf-8",
    )

    creds = resolve_kindle_credentials(global_env_file=global_env)
    assert creds.kindle_email == "global@kindle.com"
    assert creds.smtp_user == "global@gmail.com"
    assert creds.smtp_password == "global-password"

    # 3. Custom / local .env overrides global
    local_env = tmp_path / "local.env"
    local_env.write_text(
        "KINDLE_EMAIL=local@kindle.com\n",
        encoding="utf-8",
    )

    creds2 = resolve_kindle_credentials(
        custom_env_file=local_env,
        global_env_file=global_env,
    )
    assert creds2.kindle_email == "local@kindle.com"
    assert creds2.smtp_user == "global@gmail.com"

    # 4. AppSettings overrides local and global
    settings = AppSettings(
        kindle_email="settings@kindle.com",
        smtp_user="settings@gmail.com",
    )
    creds3 = resolve_kindle_credentials(
        app_settings=settings,
        custom_env_file=local_env,
        global_env_file=global_env,
    )
    assert creds3.kindle_email == "settings@kindle.com"
    assert creds3.smtp_user == "settings@gmail.com"
    assert creds3.smtp_password == "global-password"


def test_compile_epub_generation(tmp_path: Path) -> None:
    from ebook_editor.core.export.exporter import EbookExporter
    from ebook_editor.core.workspace import EbookWorkspace
    from ebook_editor.core.models import EbookMetadata

    # Setup workspace
    book_dir = tmp_path / "my-book"
    ws = EbookWorkspace(book_dir)
    ws.ensure_structure()

    meta = EbookMetadata(
        title="Testing EPUB Export",
        author="Tester",
        description="A book for testing EPUB compilation",
        finished=False,
    )
    ws.save_metadata(meta)

    # Add chapters
    ws.create_chapter("01-intro", "# Introduction\n\nThis is chapter 1.\n")
    ws.create_chapter("02-code", "# Code Chapter\n\n```python\nprint('hello')\n```\n")

    exporter = EbookExporter()
    epub_file = exporter.compile_epub(ws)

    assert epub_file.exists()
    assert epub_file.is_file()
    assert epub_file.name == "[DRAFT] Testing EPUB Export.epub"
    assert epub_file.parent == ws.dist_dir
    assert epub_file.stat().st_size > 500

    # Test finished=True removes [DRAFT] prefix
    meta.finished = True
    ws.save_metadata(meta)

    epub_finished = exporter.compile_epub(ws)
    assert epub_finished.exists()
    assert epub_finished.name == "Testing EPUB Export.epub"


def test_compile_pdf_generation(tmp_path: Path) -> None:
    from ebook_editor.core.export.exporter import EbookExporter
    from ebook_editor.core.workspace import EbookWorkspace
    from ebook_editor.core.models import EbookMetadata

    book_dir = tmp_path / "pdf-book"
    ws = EbookWorkspace(book_dir)
    ws.ensure_structure()

    meta = EbookMetadata(
        title="Testing PDF Export",
        author="Author",
        description="A book for testing PDF compilation",
        finished=False,
    )
    ws.save_metadata(meta)

    ws.create_chapter("01-intro", "# Introduction\n\nPDF chapter text.\n")
    ws.create_chapter("02-details", "# Details\n\n- Point 1\n- Point 2\n")

    exporter = EbookExporter()
    pdf_file = exporter.compile_pdf(ws)

    assert pdf_file.exists()
    assert pdf_file.is_file()
    assert pdf_file.name == "[DRAFT] Testing PDF Export.pdf"
    assert pdf_file.parent == ws.dist_dir
    assert pdf_file.stat().st_size > 1000

    # Finished=True removes [DRAFT]
    meta.finished = True
    ws.save_metadata(meta)
    pdf_finished = exporter.compile_pdf(ws)
    assert pdf_finished.exists()
    assert pdf_finished.name == "Testing PDF Export.pdf"


def test_compile_empty_workspace_error(tmp_path: Path) -> None:
    import pytest
    from ebook_editor.core.export.exporter import EbookExporter
    from ebook_editor.core.workspace import EbookWorkspace
    from ebook_editor.core.models import EbookMetadata

    book_dir = tmp_path / "empty-book"
    ws = EbookWorkspace(book_dir)
    ws.ensure_structure()
    ws.save_metadata(EbookMetadata(title="Empty Book", author="Nobody"))

    exporter = EbookExporter()
    with pytest.raises(ValueError, match="No markdown chapter files found"):
        exporter.compile_epub(ws)

    with pytest.raises(ValueError, match="No markdown chapter files found"):
        exporter.compile_pdf(ws)


def test_kindle_sender_success(tmp_path: Path, monkeypatch) -> None:
    from ebook_editor.core.export.sender import KindleSender
    from ebook_editor.core.export.credentials import KindleCredentials

    epub_file = tmp_path / "book.epub"
    epub_file.write_bytes(b"dummy epub binary content")

    creds = KindleCredentials(
        kindle_email="mydevice@kindle.com",
        smtp_user="user@gmail.com",
        smtp_password="password123",
        smtp_server="smtp.example.com",
        smtp_port=587,
    )

    sent_messages = []

    class MockSMTP:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.started_tls = False
            self.logged_in = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def ehlo(self):
            pass

        def starttls(self):
            self.started_tls = True

        def login(self, user, password):
            assert user == "user@gmail.com"
            assert password == "password123"
            self.logged_in = True

        def send_message(self, msg):
            assert self.started_tls
            assert self.logged_in
            sent_messages.append(msg)

    import smtplib
    monkeypatch.setattr(smtplib, "SMTP", MockSMTP)

    sender = KindleSender(creds)
    sender.send_epub(epub_file)

    assert len(sent_messages) == 1
    sent = sent_messages[0]
    assert sent["To"] == "mydevice@kindle.com"
    assert sent["From"] == "user@gmail.com"
    assert sent["Subject"] == "Sent from Knowledge Master"
    attachments = list(sent.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "book.epub"
    assert attachments[0].get_content() == b"dummy epub binary content"


def test_kindle_sender_errors(tmp_path: Path, monkeypatch) -> None:
    import pytest
    import smtplib
    from ebook_editor.core.export.sender import KindleSender, KindleDeliveryError
    from ebook_editor.core.export.credentials import KindleCredentials

    epub_file = tmp_path / "test.epub"
    epub_file.write_bytes(b"content")

    # 1. Incomplete credentials
    incomplete_creds = KindleCredentials(kindle_email="device@kindle.com")
    sender_incomplete = KindleSender(incomplete_creds)
    with pytest.raises(ValueError, match="missing required configuration"):
        sender_incomplete.send_epub(epub_file)

    # 2. Missing file
    valid_creds = KindleCredentials(
        kindle_email="device@kindle.com",
        smtp_user="user@gmail.com",
        smtp_password="pw",
    )
    sender_valid = KindleSender(valid_creds)
    with pytest.raises(FileNotFoundError):
        sender_valid.send_epub(tmp_path / "non_existent.epub")

    # 3. Authentication failure
    class MockFailingSMTP:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def ehlo(self):
            pass
        def starttls(self):
            pass
        def login(self, user, pw):
            raise smtplib.SMTPAuthenticationError(535, b"Authentication failed")

    monkeypatch.setattr(smtplib, "SMTP", MockFailingSMTP)
    with pytest.raises(KindleDeliveryError, match="SMTP authentication failed"):
        sender_valid.send_epub(epub_file)
