import os

import github
from github import Github


def authenticate():
    """Authenticate with GitHub using App credentials or a PAT."""
    app_id = os.environ.get("APP_ID")
    app_private_key = os.environ.get("APP_PRIVATE_KEY")
    app_installation_id = os.environ.get("APP_INSTALLATION_ID")
    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    if app_id and app_private_key and app_installation_id:
        auth = github.Auth.AppInstallationAuth(
            github.Auth.AppAuth(int(app_id), app_private_key),
            int(app_installation_id),
        )
        return Github(auth=auth)

    if gh_token:
        return Github(auth=github.Auth.Token(gh_token))

    msg = (
        "No authentication credentials found. "
        "Set GH_TOKEN or APP_ID + APP_PRIVATE_KEY + APP_INSTALLATION_ID."
    )
    raise ValueError(msg)
