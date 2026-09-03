"""Unit tests for GitService."""

from pathlib import Path
import pytest
from git import Repo

from ebook_editor.core.git_service import GitService


def test_git_service_init_and_operations(tmp_path: Path) -> None:
    workspace = tmp_path / "book"
    workspace.mkdir()

    service = GitService(workspace)
    assert service.is_git_installed()
    assert not service.is_repo()

    status = service.get_status()
    assert status.is_git_available
    assert not status.is_repo

    # Initialize repository
    service.init_repo()
    assert service.is_repo()
    assert (workspace / ".gitignore").is_file()

    # Configure repo local author for testing
    repo = Repo(workspace)
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test Author")
        config.set_value("user", "email", "author@example.com")

    # Create file
    test_file = workspace / "test.txt"
    test_file.write_text("Hello Git", encoding="utf-8")

    status = service.get_status()
    assert "test.txt" in status.untracked_files

    # Stage file
    service.stage_file("test.txt")
    status = service.get_status()
    assert "test.txt" in status.staged_files

    # Unstage file
    service.unstage_file("test.txt")
    status = service.get_status()
    assert "test.txt" in status.untracked_files

    # Stage all and commit
    service.stage_all()
    commit = service.create_commit("Initial test commit")
    assert commit.hexsha is not None
    assert commit.message == "Initial test commit"

    log = service.get_commit_log()
    assert len(log) == 1
    assert log[0].message == "Initial test commit"

    # Modify file and discard changes
    test_file.write_text("Modified text", encoding="utf-8")
    status = service.get_status()
    assert "test.txt" in status.unstaged_files

    service.discard_changes("test.txt")
    assert test_file.read_text(encoding="utf-8") == "Hello Git"
