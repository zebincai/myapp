# Repository Guidelines

## Project Structure & Module Organization

- This repository is a lightweight scaffold with contributor guidance and development artifacts.
- Add new code in a predictable top-level layout so future contributors can navigate it quickly.

Directory guide:

- `artifacts/` for checked-in support artifacts. See `artifacts/README.md` before adding files here.
- `src/` for application source code.
- `tests/` for automated tests that mirror `src/` module names.
- `assets/` for static files such as images, fonts, and fixtures.
- `docs/` for design documents and project notes.
- `scripts/` for repeatable project commands that do not belong in the application runtime.

- Keep generated output, dependency directories, and local environment files out of version control.
- Keep module-specific API, setup, run, and test documentation beside the related module, not in the root guide.

## Docs

- Store all design documents under `docs/design/`.
- Prefix each design doc filename with its creation date.
- Use the filename format `YYYY-MM-DD-topic-name.md`, for example `2026-06-03-backend-user-crud-design.md`.
- Include `Owner`, `Create Date`, and `Update Date` near the top of each design doc.

## Build, Test, and Development Commands

- Keep module-specific build, test, and development commands in that module's `README.md` or `AGENTS.md`.
- Add root-level commands here only when they apply to the whole repository.
- Before adding a command, make sure it works from the repository root or clearly document the required working directory.

## Coding Style & Naming Conventions

- Use clear, descriptive names and keep module boundaries small.
- Prefer lowercase directory names, such as `src/components/` or `src/services/`.
- Match file naming to the selected language and framework. For example, use `PascalCase` for React components and `snake_case` for Python modules.
- Adopt a formatter and linter as soon as the primary language is chosen.
- Keep formatting automated rather than relying on manual review.

## Testing Guidelines

- Place tests under `tests/` or the framework-standard location.
- Make test files clearly map to the code under test, for example `tests/user_service.test.ts` for `src/user_service.ts`.
- Add focused unit tests for core logic.
- Add integration tests for user-facing workflows or external boundaries.
- Run the full test suite before opening a pull request.
- For artifact-only updates, verify that documented paths exist and that `artifacts/README.md` describes any new checked-in artifacts.

## Commit & Pull Request Guidelines

- No local git history is available, so no existing commit convention can be inferred.
- Use short, imperative commit messages.
- Prefer Conventional Commits, such as `feat: add user profile view` or `fix: handle missing config`.
- Pull requests should include a concise description, linked issue when available, and test results.
- Include screenshots for UI changes.

## Agent-Specific Instructions

- Keep changes scoped to the requested task.
- Do not introduce project tooling, dependencies, or directory structure unless the change requires it.
- Format guidance sections as short bullet points instead of long paragraph instructions.
- When adding or changing a module, update that module's `README.md` or `AGENTS.md` with its API notes, commands, and test information.
- When adding or changing files under `artifacts/`, update `artifacts/README.md` with the artifact path, purpose, and any verification steps.
