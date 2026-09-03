"""Git version control wrapper with graceful degradation."""

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import git
    from git import Repo, InvalidGitRepositoryError, NoSuchPathError
    _GIT_IMPORT_ERROR = None
except Exception as e:  # pragma: no cover
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception
    NoSuchPathError = Exception
    _GIT_IMPORT_ERROR = str(e)


DEFAULT_GITIGNORE_CONTENT = """# Operating System Files
.DS_Store
Thumbs.db
*.tmp
*.swp

# Application cache
.cache/
__pycache__/
"""


@dataclass
class GitCommitInfo:
    """Represents a simplified Git commit log entry."""

    hexsha: str
    short_sha: str
    message: str
    author: str
    date: datetime


@dataclass
class GitStatusResult:
    """Summary of current Git repository working tree and capability status."""

    is_git_available: bool = True
    is_repo: bool = False
    has_identity: bool = True
    author_name: str | None = None
    author_email: str | None = None
    error_message: str | None = None
    branch_name: str = "main"
    staged_files: list[str] = field(default_factory=list)
    unstaged_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)


class GitService:
    """Provides non-blocking Git operations for an ebook directory."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path.expanduser().resolve()
        self._repo: Any | None = None

    @classmethod
    def is_git_installed(cls) -> bool:
        """Check if Git binary and Python module are available."""
        if _GIT_IMPORT_ERROR is not None:
            return False
        return shutil.which("git") is not None

    def is_repo(self) -> bool:
        """Check if workspace contains a .git directory."""
        return (self.workspace_path / ".git").is_dir()

    def _get_repo(self) -> Any:
        """Get or initialize the GitPython Repo instance."""
        if self._repo is None:
            self._repo = Repo(self.workspace_path)
        return self._repo

    def get_user_identity(self) -> tuple[str | None, str | None]:
        """Read global or repository git user.name and user.email."""
        if not self.is_git_installed():
            return None, None
        try:
            reader = git.GitConfigParser()
            name = reader.get_value("user", "name", fallback=None)
            email = reader.get_value("user", "email", fallback=None)
            if self.is_repo():
                try:
                    repo = self._get_repo()
                    repo_reader = repo.config_reader()
                    name = repo_reader.get_value("user", "name", fallback=name)
                    email = repo_reader.get_value("user", "email", fallback=email)
                except Exception:
                    pass
            return (str(name) if name else None, str(email) if email else None)
        except Exception:
            return None, None

    def get_status(self) -> GitStatusResult:
        """Inspect and return current Git repository state gracefully."""
        if not self.is_git_installed():
            return GitStatusResult(
                is_git_available=False,
                error_message="Git binary is not installed or not found in system PATH.",
            )

        name, email = self.get_user_identity()
        has_identity = bool(name and email)

        if not self.is_repo():
            return GitStatusResult(
                is_git_available=True,
                is_repo=False,
                has_identity=has_identity,
                author_name=name,
                author_email=email,
            )

        try:
            repo = self._get_repo()
            branch = "HEAD"
            try:
                branch = repo.active_branch.name
            except TypeError:
                # Detached HEAD or empty repo
                branch = "main"

            staged: list[str] = []
            unstaged: list[str] = []

            # Check staged changes
            try:
                diff_staged = repo.index.diff("HEAD")
                staged = [d.a_path or d.b_path for d in diff_staged if (d.a_path or d.b_path)]
            except Exception:
                # In empty repo, diffing HEAD fails; check index against empty tree
                try:
                    staged = [entry[0] for entry in repo.index.entries.keys()]
                except Exception:
                    pass

            # Check unstaged working tree changes
            diff_unstaged = repo.index.diff(None)
            unstaged = [d.a_path or d.b_path for d in diff_unstaged if (d.a_path or d.b_path)]

            # Check untracked files
            untracked = repo.untracked_files

            return GitStatusResult(
                is_git_available=True,
                is_repo=True,
                has_identity=has_identity,
                author_name=name,
                author_email=email,
                branch_name=branch,
                staged_files=staged,
                unstaged_files=unstaged,
                untracked_files=untracked,
            )
        except Exception as e:
            return GitStatusResult(
                is_git_available=True,
                is_repo=True,
                has_identity=has_identity,
                error_message=str(e),
            )

    def init_repo(self) -> None:
        """Initialize a new Git repository and generate a default .gitignore."""
        if not self.is_git_installed():
            raise RuntimeError("Git is not installed on this system.")

        repo = Repo.init(self.workspace_path)
        self._repo = repo

        gitignore_file = self.workspace_path / ".gitignore"
        if not gitignore_file.exists():
            gitignore_file.write_text(DEFAULT_GITIGNORE_CONTENT, encoding="utf-8")

    def stage_file(self, path: str) -> None:
        """Stage a single file into the Git index."""
        repo = self._get_repo()
        repo.git.add(path)

    def unstage_file(self, path: str) -> None:
        """Unstage a single file from the Git index."""
        repo = self._get_repo()
        try:
            repo.git.restore("--staged", path)
        except Exception:
            repo.git.reset("HEAD", "--", path)

    def stage_all(self) -> None:
        """Stage all modified, deleted, and untracked files."""
        repo = self._get_repo()
        repo.git.add(A=True)

    def unstage_all(self) -> None:
        """Unstage all files from the Git index."""
        repo = self._get_repo()
        repo.git.reset()

    def discard_changes(self, path: str) -> None:
        """Discard changes in a modified or untracked file."""
        repo = self._get_repo()
        target = self.workspace_path / path
        if path in repo.untracked_files:
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        else:
            repo.git.checkout("--", path)

    def create_commit(self, message: str) -> GitCommitInfo:
        """Create a new Git commit with the provided message."""
        if not message.strip():
            raise ValueError("Commit message cannot be empty.")
        repo = self._get_repo()
        commit = repo.index.commit(message.strip())
        return GitCommitInfo(
            hexsha=commit.hexsha,
            short_sha=commit.hexsha[:7],
            message=commit.message.strip(),
            author=commit.author.name,
            date=datetime.fromtimestamp(commit.committed_date, timezone.utc),
        )

    def get_commit_log(self, limit: int = 20) -> list[GitCommitInfo]:
        """Fetch the most recent commits in reverse chronological order."""
        if not self.is_repo():
            return []
        try:
            repo = self._get_repo()
            commits = list(repo.iter_commits(max_count=limit))
            return [
                GitCommitInfo(
                    hexsha=c.hexsha,
                    short_sha=c.hexsha[:7],
                    message=c.message.strip(),
                    author=c.author.name,
                    date=datetime.fromtimestamp(c.committed_date, timezone.utc),
                )
                for c in commits
            ]
        except Exception:
            return []
