from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoopConfig:
    issue_label: str
    issue_label_color: str
    issue_label_description: str
    issue_title: str
    issue_title_prefix: str
    copilot_assignee: str
    human_assignees: list[str]


def load_config(config_path: Path) -> LoopConfig:
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return LoopConfig(
        issue_label=raw["issue_label"],
        issue_label_color=raw["issue_label_color"],
        issue_label_description=raw["issue_label_description"],
        issue_title=raw["issue_title"],
        issue_title_prefix=raw["issue_title_prefix"],
        copilot_assignee=raw["copilot_assignee"],
        human_assignees=list(raw.get("human_assignees", [])),
    )


def github_request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("User-Agent", "pic-agentic-workflow-relativistic-loop")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        request.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(request) as response:
        text = response.read().decode("utf-8")
        if not text:
            return None
        return json.loads(text)


def github_request_optional(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    try:
        return 200, github_request(method, url, token, payload)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        parsed = json.loads(body) if body else None
        return error.code, parsed


def build_issue_body(config: LoopConfig) -> str:
    return f"""This issue was created automatically by the relativistic agent loop.

Use [agent/prompts/relativistic_research.md](agent/prompts/relativistic_research.md) as the governing brief.

Objective:
- Keep advancing this repository toward a momentum-space, formally relativistic 1D3V electrostatic PIC workflow staging path for later upstream use in JAX-in-Cell.

Execution requirements:
1. Inspect the current repository state, latest reports, and any recent merged PRs.
2. Select the single highest-value next bounded milestone.
3. Ground the milestone in relevant scientific literature where needed.
4. Make only the smallest reviewable change required for that milestone.
5. Add validation, diagnostics, tests, or a bounded research summary.
6. Open a PR against `main`.
7. End the PR body with a section named `Next recommended milestone`.

Guardrails:
- Work only in this repository.
- Do not modify JAX-in-Cell directly here.
- Do not weaken workflow security, runner restrictions, or branch protection.
- Do not claim full relativistic capability unless it is actually implemented and validated upstream.

Loop behavior:
- When this issue is completed and closed, the automation will create the next milestone issue.
- Keep the scope to one milestone only.

Expected labels and assignees:
- label: `{config.issue_label}`
- assignees: `{config.copilot_assignee}` and maintainers listed in `agent/policies/relativistic_loop.toml`
"""


def ensure_label(api_root: str, repo: str, token: str, config: LoopConfig) -> None:
    label_url = (
        f"{api_root}/repos/{repo}/labels/"
        f"{urllib.parse.quote(config.issue_label, safe='')}"
    )
    status_code, _ = github_request_optional("GET", label_url, token)
    if status_code == 200:
        return
    if status_code != 404:
        raise RuntimeError(f"Unexpected label lookup status: {status_code}")

    create_url = f"{api_root}/repos/{repo}/labels"
    github_request(
        "POST",
        create_url,
        token,
        {
            "name": config.issue_label,
            "color": config.issue_label_color,
            "description": config.issue_label_description,
        },
    )


def list_open_loop_issues(api_root: str, repo: str, token: str, config: LoopConfig) -> list[dict[str, Any]]:
    issues_url = (
        f"{api_root}/repos/{repo}/issues?state=open&labels="
        f"{urllib.parse.quote(config.issue_label, safe='')}&per_page=100"
    )
    issues = github_request("GET", issues_url, token)
    return [
        issue
        for issue in issues
        if "pull_request" not in issue and issue["title"].startswith(config.issue_title_prefix)
    ]


def ensure_issue_assignees(api_root: str, repo: str, token: str, issue_number: int, assignees: list[str]) -> None:
    if not assignees:
        return

    assignee_url = f"{api_root}/repos/{repo}/issues/{issue_number}/assignees"
    for assignee in assignees:
        status_code, payload = github_request_optional(
            "POST",
            assignee_url,
            token,
            {"assignees": [assignee]},
        )
        actual_assignees: set[str] = set()
        if isinstance(payload, dict):
            actual_assignees = {
                entry.get("login", "")
                for entry in payload.get("assignees", [])
                if isinstance(entry, dict)
            }

        if status_code == 200 and assignee in actual_assignees:
            continue

        message = ""
        if isinstance(payload, dict):
            message = payload.get("message", "")
        if not message and status_code == 200:
            message = "API call succeeded, but the assignee was not actually attached to the issue"
        print(f"Warning: could not assign '{assignee}' to issue #{issue_number}: {message}")


def create_issue(api_root: str, repo: str, token: str, config: LoopConfig) -> dict[str, Any]:
    create_url = f"{api_root}/repos/{repo}/issues"
    issue = github_request(
        "POST",
        create_url,
        token,
        {
            "title": config.issue_title,
            "body": build_issue_body(config),
            "labels": [config.issue_label],
        },
    )
    issue_number = int(issue["number"])
    ensure_issue_assignees(
        api_root,
        repo,
        token,
        issue_number,
        [config.copilot_assignee, *config.human_assignees],
    )
    return issue


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure the relativistic Copilot milestone loop has an open issue.")
    parser.add_argument("--dry-run", action="store_true", help="Render the issue body and planned action without calling GitHub.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(Path("agent/policies/relativistic_loop.toml"))

    if args.dry_run:
        print(config.issue_title)
        print()
        print(build_issue_body(config))
        return 0

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    api_root = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")

    if not token:
        print("Missing GITHUB_TOKEN", file=sys.stderr)
        return 1
    if not repo:
        print("Missing GITHUB_REPOSITORY", file=sys.stderr)
        return 1

    ensure_label(api_root, repo, token, config)
    open_issues = list_open_loop_issues(api_root, repo, token, config)

    if open_issues:
        chosen_issue = sorted(open_issues, key=lambda issue: issue["number"])[0]
        issue_number = int(chosen_issue["number"])
        print(f"Found existing loop issue #{issue_number}: {chosen_issue['title']}")
        ensure_issue_assignees(
            api_root,
            repo,
            token,
            issue_number,
            [config.copilot_assignee, *config.human_assignees],
        )
        return 0

    issue = create_issue(api_root, repo, token, config)
    print(f"Created new loop issue #{issue['number']}: {issue['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())