"""Kindle and SMTP credential models and waterfall resolution service."""

import os
from pathlib import Path
from pydantic import BaseModel, Field
import dotenv

from ebook_editor.core.models import AppSettings

GLOBAL_EBOOK_MAKER_ENV = Path.home() / ".config" / "ebook-maker" / ".env"


class KindleCredentials(BaseModel):
    """Holds configuration and credentials required to send EPUB files to Kindle via SMTP."""

    kindle_email: str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

    def is_configured(self) -> bool:
        """Check whether all essential credentials are present and non-empty."""
        return bool(
            self.kindle_email
            and self.kindle_email.strip()
            and self.smtp_user
            and self.smtp_user.strip()
            and self.smtp_password
            and self.smtp_password.strip()
        )

    def missing_fields(self) -> list[str]:
        """Return the names of missing required configuration fields."""
        missing: list[str] = []
        if not self.kindle_email or not self.kindle_email.strip():
            missing.append("kindle_email")
        if not self.smtp_user or not self.smtp_user.strip():
            missing.append("smtp_user")
        if not self.smtp_password or not self.smtp_password.strip():
            missing.append("smtp_password")
        return missing


def resolve_kindle_credentials(
    app_settings: AppSettings | None = None,
    custom_env_file: Path | None = None,
    global_env_file: Path | None = None,
) -> KindleCredentials:
    """
    Resolve Kindle and SMTP credentials using a prioritized waterfall cascade:
      1. Explicit values in AppSettings
      2. Values in custom/local .env file
      3. Values in global ~/.config/ebook-maker/.env (reusing existing user credentials)
      4. System environment variables (os.environ)
    """
    # 1. Start with system environment variables
    env_vars = os.environ

    kindle_email = env_vars.get("KINDLE_EMAIL")
    smtp_user = env_vars.get("SMTP_USER")
    smtp_password = env_vars.get("SMTP_PASSWORD")
    smtp_server = env_vars.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_raw = env_vars.get("SMTP_PORT", "587")

    # 2. Layer global ebook-maker .env if present
    global_path = global_env_file or GLOBAL_EBOOK_MAKER_ENV
    if global_path.exists():
        global_values = dotenv.dotenv_values(global_path)
        kindle_email = global_values.get("KINDLE_EMAIL") or kindle_email
        smtp_user = global_values.get("SMTP_USER") or smtp_user
        smtp_password = global_values.get("SMTP_PASSWORD") or smtp_password
        smtp_server = global_values.get("SMTP_SERVER") or smtp_server
        smtp_port_raw = global_values.get("SMTP_PORT") or smtp_port_raw

    # 3. Layer local/custom .env if present
    if custom_env_file and custom_env_file.exists():
        local_values = dotenv.dotenv_values(custom_env_file)
        kindle_email = local_values.get("KINDLE_EMAIL") or kindle_email
        smtp_user = local_values.get("SMTP_USER") or smtp_user
        smtp_password = local_values.get("SMTP_PASSWORD") or smtp_password
        smtp_server = local_values.get("SMTP_SERVER") or smtp_server
        smtp_port_raw = local_values.get("SMTP_PORT") or smtp_port_raw

    # 4. Layer explicit AppSettings if provided
    if app_settings:
        if app_settings.kindle_email:
            kindle_email = app_settings.kindle_email
        if app_settings.smtp_user:
            smtp_user = app_settings.smtp_user
        if app_settings.smtp_password:
            smtp_password = app_settings.smtp_password
        if app_settings.smtp_server:
            smtp_server = app_settings.smtp_server
        if app_settings.smtp_port:
            smtp_port_raw = str(app_settings.smtp_port)

    try:
        smtp_port = int(smtp_port_raw)
    except (ValueError, TypeError):
        smtp_port = 587

    return KindleCredentials(
        kindle_email=kindle_email.strip() if kindle_email else None,
        smtp_user=smtp_user.strip() if smtp_user else None,
        smtp_password=smtp_password.strip() if smtp_password else None,
        smtp_server=smtp_server.strip() if smtp_server else "smtp.gmail.com",
        smtp_port=smtp_port,
    )
