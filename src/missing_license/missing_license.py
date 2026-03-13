import importlib.resources
import os
import sys

from github import GithubException

from missing_license.auth import authenticate


def get_license(repo):
    """Return True if the repo has a license (via API or file)."""
    if repo.license is not None:
        return True

    for filename in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
        try:
            repo.get_contents(filename)
            return True
        except GithubException:
            pass

    return False


def has_existing_issue(repo, issue_title, bot_login):
    """Return True if any issue (open or closed) with the given title exists."""
    try:
        for issue in repo.get_issues(state="all", creator=bot_login):
            if issue.title == issue_title:
                return True
    except GithubException:
        pass
    return False


def process_repo(
    repo, issue_title, issue_body, issue_labels, exempt_repos, dry_run, bot_login
):
    """Process a single repo. Returns a status string."""
    if repo.archived:
        return "archived"

    if repo.name in exempt_repos:
        return "exempt"

    if get_license(repo):
        return "licensed"

    if has_existing_issue(repo, issue_title, bot_login):
        return "already_notified"

    if not dry_run:
        labels = [label.strip() for label in issue_labels.split(",") if label.strip()]
        body = issue_body.replace("{repo_name}", repo.name)
        repo.create_issue(title=issue_title, body=body, labels=labels)

    return "dry_run" if dry_run else "issue_opened"


def main():
    gh = authenticate()

    organization = os.environ.get("ORGANIZATION", "")
    issue_title = os.environ.get("ISSUE_TITLE", "TODO")
    issue_body_path = os.environ.get("ISSUE_BODY_PATH", "")
    if issue_body_path:
        with open(issue_body_path) as f:
            issue_body = f.read()
    else:
        issue_body = (
            importlib.resources.files("missing_license")
            .joinpath("issue_body.md")
            .read_text()
        )
    issue_labels = os.environ.get("ISSUE_LABELS", "missing-license")
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    exempt_repos_str = os.environ.get("EXEMPT_REPOS", "")
    exempt_repos = {r.strip() for r in exempt_repos_str.split(",") if r.strip()}

    if not organization:
        print("ERROR: ORGANIZATION environment variable is required")
        sys.exit(1)

    bot_login = gh.get_user().login
    try:
        org = gh.get_organization(organization)
    except GithubException as e:
        if e.status == 404:
            org = gh.get_user(organization)
        else:
            raise

    results = {
        "archived": [],
        "exempt": [],
        "licensed": [],
        "already_notified": [],
        "issue_opened": [],
        "dry_run": [],
    }

    for repo in org.get_repos(type="public"):
        status = process_repo(
            repo,
            issue_title,
            issue_body,
            issue_labels,
            exempt_repos,
            dry_run,
            bot_login,
        )
        results[status].append(repo.name)

    print("\n## Missing License Summary\n")
    print("| Status | Count |")
    print("|--------|-------|")
    print(f"| Issues opened | {len(results['issue_opened'])} |")
    print(f"| Dry run (would open) | {len(results['dry_run'])} |")
    print(f"| Already notified | {len(results['already_notified'])} |")
    print(f"| Licensed | {len(results['licensed'])} |")
    print(f"| Archived (skipped) | {len(results['archived'])} |")
    print(f"| Exempt (skipped) | {len(results['exempt'])} |")

    if results["issue_opened"]:
        print("\n### Issues opened on:")
        for name in results["issue_opened"]:
            print(f"- {name}")

    if results["dry_run"]:
        print("\n### Would open issues on (dry run):")
        for name in results["dry_run"]:
            print(f"- {name}")


if __name__ == "__main__":
    main()
