# Security Model

This repository is public but uses a narrow trust split for automation.

## Trust Split

- Public `push` and `pull_request` validation stays on GitHub-hosted runners.
- Issue-comment parsing stays on GitHub-hosted runners.
- Only trusted optimization workflows are allowed to target the self-hosted runner.
- Optimization state is committed directly to `main` by maintainer-controlled scheduled and dispatch workflows.

## Self-Hosted Runner Safety Rules

The self-hosted runner is only appropriate if all of the following remain true:

1. Public PRs never execute on the self-hosted runner.
2. `main` is branch-protected and only trusted automation tokens or maintainers can bypass that protection.
3. Only a short allowlist of maintainers can manually dispatch self-hosted workflows.
4. The organization runner group is restricted to this repository or a very small trusted set.
5. The runner group allows this public repository only because the workflows routed to it are maintainer-controlled and non-PR.
6. The runner group should be restricted to selected workflows if the organization supports that setting.

## Required GitHub Settings

Recommended repository settings:

1. Protect `main` and require pull requests before merge.
2. Require at least one approval, ideally with CODEOWNERS review.
3. Disable force pushes and branch deletion on `main`.
4. Keep `Allow auto-merge` disabled.
5. Restrict Actions to GitHub-authored and explicitly approved actions.
6. Enable SHA pinning for Actions if your organization policy supports it.
7. Enable secret scanning and push protection.
8. Keep self-hosted workflows limited to `workflow_dispatch` and `schedule` only.

Recommended organization Actions settings:

1. Put the Mac mini runner in a dedicated runner group, not the general default group.
2. Allow only this repository to use that runner group.
3. Allow public repositories only if you intentionally want this public repo to use the runner.
4. Restrict the runner group to the exact optimization workflows when possible.

## Threat Model

The main malware risk for a public repository with a self-hosted runner is untrusted code execution on that runner. This repository reduces that risk by keeping PR and issue-comment execution off the self-hosted runner. The remaining critical control is GitHub settings: branch protection, limited write access, and a narrowly scoped runner group.
