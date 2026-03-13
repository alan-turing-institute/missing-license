import importlib.resources
from pathlib import Path

from missing_license.missing_license import (
    get_license,
    has_existing_issue,
    process_repo,
)
from tests.conftest import make_issue, make_repo

ISSUE_TITLE = "This repository has no license"
ISSUE_BODY = "Please add a license to {repo_name}."
ISSUE_LABELS = "missing-license"
BOT_LOGIN = "test-bot"


class TestGetLicense:
    def test_licensed_via_api(self):
        repo = make_repo("my-repo", has_license_api=True)
        assert get_license(repo) is True

    def test_licensed_via_license_file(self):
        repo = make_repo("my-repo", license_files=["LICENSE"])
        assert get_license(repo) is True

    def test_licensed_via_license_md(self):
        repo = make_repo("my-repo", license_files=["LICENSE.md"])
        assert get_license(repo) is True

    def test_licensed_via_license_txt(self):
        repo = make_repo("my-repo", license_files=["LICENSE.txt"])
        assert get_license(repo) is True

    def test_unlicensed(self):
        repo = make_repo("my-repo")
        assert get_license(repo) is False


class TestHasExistingIssue:
    def test_open_issue_exists(self):
        issue = make_issue(ISSUE_TITLE, state="open")
        repo = make_repo("my-repo", issues=[issue])
        assert has_existing_issue(repo, ISSUE_TITLE, BOT_LOGIN) is True

    def test_closed_issue_exists(self):
        issue = make_issue(ISSUE_TITLE, state="closed")
        repo = make_repo("my-repo", issues=[issue])
        assert has_existing_issue(repo, ISSUE_TITLE, BOT_LOGIN) is True

    def test_no_issue_exists(self):
        repo = make_repo("my-repo", issues=[])
        assert has_existing_issue(repo, ISSUE_TITLE, BOT_LOGIN) is False

    def test_different_title_not_matched(self):
        issue = make_issue("Some other issue")
        repo = make_repo("my-repo", issues=[issue])
        assert has_existing_issue(repo, ISSUE_TITLE, BOT_LOGIN) is False


class TestProcessRepo:
    def _run(self, repo, dry_run=False, exempt_repos=None):
        return process_repo(
            repo,
            ISSUE_TITLE,
            ISSUE_BODY,
            ISSUE_LABELS,
            exempt_repos or set(),
            dry_run,
            BOT_LOGIN,
        )

    def test_archived_repo_skipped(self):
        repo = make_repo("my-repo", archived=True)
        assert self._run(repo) == "archived"

    def test_exempt_repo_skipped(self):
        repo = make_repo("my-repo")
        assert self._run(repo, exempt_repos={"my-repo"}) == "exempt"

    def test_licensed_repo_skipped(self):
        repo = make_repo("my-repo", has_license_api=True)
        assert self._run(repo) == "licensed"

    def test_already_notified_open_issue(self):
        issue = make_issue(ISSUE_TITLE, state="open")
        repo = make_repo("my-repo", issues=[issue])
        assert self._run(repo) == "already_notified"

    def test_already_notified_closed_issue(self):
        issue = make_issue(ISSUE_TITLE, state="closed")
        repo = make_repo("my-repo", issues=[issue])
        assert self._run(repo) == "already_notified"

    def test_unlicensed_opens_issue(self):
        repo = make_repo("my-repo")
        assert self._run(repo) == "issue_opened"
        repo.create_issue.assert_called_once_with(
            title=ISSUE_TITLE,
            body=ISSUE_BODY.replace("{repo_name}", "my-repo"),
            labels=["missing-license"],
        )

    def test_dry_run_does_not_open_issue(self):
        repo = make_repo("my-repo")
        assert self._run(repo, dry_run=True) == "dry_run"
        repo.create_issue.assert_not_called()

    def test_archived_takes_priority_over_exempt(self):
        repo = make_repo("my-repo", archived=True)
        assert self._run(repo, exempt_repos={"my-repo"}) == "archived"


class TestIssueBodyLoading:
    def test_bundled_body_loaded_when_no_path_set(self, monkeypatch):
        monkeypatch.delenv("ISSUE_BODY_PATH", raising=False)
        bundled = (
            importlib.resources.files("missing_license")
            .joinpath("issue_body.md")
            .read_text()
        )
        assert "{repo_name}" in bundled

    def test_custom_body_loaded_from_file(self, tmp_path):
        body_file = tmp_path / "custom.md"
        body_file.write_text("Custom body for {repo_name}.")
        assert Path(str(body_file)).read_text() == "Custom body for {repo_name}."
