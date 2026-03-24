# missing-license

[![CI](https://github.com/alan-turing-institute/missing-license/actions/workflows/ci.yml/badge.svg)](https://github.com/alan-turing-institute/missing-license/actions/workflows/ci.yml)

A GitHub Action that scans an organisation for public repositories without a license and opens issues to notify owners.

## Usage

Add a workflow file to your repository:

```yaml
name: Check for missing licenses

on:
  schedule:
    - cron: "0 9 * * 1"  # every Monday at 09:00 UTC
  workflow_dispatch:

jobs:
  missing-license:
    runs-on: ubuntu-latest
    steps:
      - uses: alan-turing-institute/missing-license@v1
        with:
          gh_token: ${{ secrets.GITHUB_TOKEN }}
          organization: my-org
```

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `gh_token` | Yes* | — | GitHub token or PAT with repo and issues write access |
| `app_id` | Yes* | — | GitHub App ID (alternative to `gh_token`) |
| `app_private_key` | Yes* | — | GitHub App private key PEM |
| `app_installation_id` | Yes* | — | GitHub App installation ID |
| `organization` | Yes | — | GitHub organisation to scan |
| `issue_title` | No | `Adding a license to your repository` | Title for issues opened on unlicensed repos |
| `issue_body_path` | No | bundled template | Path to a markdown file used as the issue body. Supports `{repo_name}` placeholder |
| `exempt_repos` | No | — | Comma-separated list of repository names to skip |
| `dry_run` | No | `false` | If `true`, log findings but do not open issues |

*Provide either `gh_token` or all three of `app_id`, `app_private_key`, and `app_installation_id`.

### Authentication

**Personal access token (PAT):**

```yaml
with:
  gh_token: ${{ secrets.MY_PAT }}
  organization: my-org
```

**GitHub App:**

```yaml
with:
  app_id: ${{ secrets.APP_ID }}
  app_private_key: ${{ secrets.APP_PRIVATE_KEY }}
  app_installation_id: ${{ secrets.APP_INSTALLATION_ID }}
  organization: my-org
```

### Custom issue body

By default the action uses the `issue_body.md` found at `src/missing_license/issue_body.md`. To use your own template, add a markdown file to your repo and pass its path:

```yaml
with:
  gh_token: ${{ secrets.GITHUB_TOKEN }}
  organization: my-org
  issue_body_path: .github/missing-license-body.md
```

The template supports a `{repo_name}` placeholder which is replaced with the name of each unlicensed repository.

### Behaviour

- Archived repositories are skipped.
- Repositories listed in `exempt_repos` are skipped.
- If a matching issue (open **or** closed) already exists on a repository, no new issue is opened. A closed issue is treated as an intentional choice to remain unlicensed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.

## License

Distributed under the terms of the [MIT license](LICENSE).

## Disclaimer

This action has been developed with Claude code.
