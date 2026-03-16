from unittest.mock import MagicMock

from github import GithubException


def make_issue(title, state="open"):
    issue = MagicMock()
    issue.title = title
    issue.state = state
    return issue


def make_repo(
    name,
    archived=False,
    fork=False,
    has_license_api=False,
    license_files=None,
    issues=None,
):
    """Factory for mock Repository objects."""
    repo = MagicMock()
    repo.name = name
    repo.archived = archived
    repo.fork = fork
    repo.license = MagicMock() if has_license_api else None

    license_files = license_files or []

    def get_contents(path):
        if path in license_files:
            return MagicMock()
        raise GithubException(404, {"message": "Not Found"}, None)

    repo.get_contents = get_contents
    repo.get_issues.return_value = iter(issues or [])
    repo.create_issue = MagicMock()

    return repo
