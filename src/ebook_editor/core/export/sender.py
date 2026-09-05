"""Kindle email delivery service sending EPUB files via SMTP."""

from email.message import EmailMessage
from pathlib import Path
import smtplib

from ebook_editor.core.export.credentials import KindleCredentials


class KindleDeliveryError(Exception):
    """Raised when an error occurs during EPUB email transmission."""
    pass


class KindleSender:
    """Manages email composition and SMTP transmission to Amazon Kindle addresses."""

    def __init__(self, credentials: KindleCredentials) -> None:
        self.credentials = credentials

    def send_epub(self, epub_path: Path) -> None:
        """
        Send an EPUB file to the configured Kindle email address via SMTP TLS.

        Raises:
            ValueError: If required credentials are missing.
            FileNotFoundError: If the EPUB file does not exist on disk.
            KindleDeliveryError: If SMTP connection, authentication, or delivery fails.
        """
        if not self.credentials.is_configured():
            missing = ", ".join(self.credentials.missing_fields())
            raise ValueError(f"Cannot send to Kindle: missing required configuration ({missing}).")

        if not epub_path.exists() or not epub_path.is_file():
            raise FileNotFoundError(f"EPUB file to send does not exist: {epub_path}")

        # Construct email message
        msg = EmailMessage()
        msg["Subject"] = "Sent from Knowledge Master"
        msg["From"] = self.credentials.smtp_user
        msg["To"] = self.credentials.kindle_email
        msg.set_content("Please find attached your EPUB document sent from Knowledge Master.")

        epub_bytes = epub_path.read_bytes()
        msg.add_attachment(
            epub_bytes,
            maintype="application",
            subtype="epub+zip",
            filename=epub_path.name,
        )

        try:
            with smtplib.SMTP(self.credentials.smtp_server, self.credentials.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.credentials.smtp_user, self.credentials.smtp_password)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError as e:
            raise KindleDeliveryError(
                f"SMTP authentication failed for {self.credentials.smtp_user}. "
                "Ensure your password or Gmail App Password is correct."
            ) from e
        except Exception as e:
            raise KindleDeliveryError(f"Failed to transmit EPUB to Kindle via SMTP: {e}") from e
