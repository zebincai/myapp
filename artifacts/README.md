# Artifacts

This folder stores repository artifacts that support development, builds, deployment, or documentation but are not application source code.

## Contents

- `docker/dev.dockerfile`: Development container image based on Ubuntu 24.04. It installs common tools, creates a non-root `dev` user, uses `/workspace` as the working directory, and starts Bash by default.

## Guidelines

- Keep artifact paths stable once other tools or documentation reference them.
- Add a short note here when introducing a new artifact.
- Keep generated outputs out of this folder unless they are intentionally checked in.
- Prefer lowercase directory names, such as `docker/`, `ci/`, or `release/`.

## Verification

There is no project build or test runner yet. For now, verify artifact changes by checking that referenced files exist and that paths in this README match the repository layout.
