# Repository Context Engineering

- Owner: Codex
- Create Date: 2026-06-04
- Update Date: 2026-06-04

## Overview

This repository demonstrates a lightweight approach to repository context engineering: keep project knowledge in the repository, organize it like code, and make it readable by both humans and agents.

The goal is not to add a large documentation process. The goal is to make the repository itself carry enough context for a teammate or coding agent to understand where things belong, what has already been decided, and how to make the next change without asking for tribal knowledge.

## What This Repository Shows

- Documentation is stored as versioned files, not scattered across chat history or private notes.
- The directory tree separates source code, tests, design notes, static assets, scripts, and support artifacts.
- Root-level guidance explains the repository contract.
- Module-level documentation explains local APIs, commands, and test notes.
- Design documents are dated and kept under `docs/design/`.
- Agent instructions live in `AGENTS.md`, so coding agents can read the same contribution rules as people.

## Theme 1: Documentation as Code

Documentation in this repo is treated as part of the codebase.
Examples:

- `README.md` gives the top-level entry point.
- `AGENTS.md` defines repository rules, naming conventions, testing expectations, and agent-specific instructions.
- `docs/design/2026-06-03-backend-user-crud-design.md` captures backend design decisions before or alongside implementation.
- `src/backend/README.md` keeps backend-specific run and API notes beside backend code.
- `artifacts/README.md` explains checked-in support artifacts and how to verify them.

This gives the team several benefits:

- Context changes can be reviewed in pull requests.
- Design decisions have a stable path and filename.
- Agents can read the same source of truth as developers.
- New teammates can onboard from files in the repo instead of asking where information lives.

## Theme 2: Tree-Shaped Organization

The repository uses a predictable top-level layout:

| Path | Purpose |
| --- | --- |
| `src/` | Application source code. |
| `tests/` | Automated tests that mirror source modules. |
| `docs/` | Design documents and project notes. |
| `docs/design/` | Dated design documents. |
| `assets/` | Static files such as images, fonts, and fixtures. |
| `artifacts/` | Checked-in support artifacts. |
| `scripts/` | Repeatable project commands outside runtime code. |

The important point is that the tree itself communicates ownership and intent. A contributor does not need to guess whether a design note belongs next to runtime code, in a root document, or in an external wiki.

The same pattern scales down into modules. For example, backend-specific notes live under `src/backend/README.md` instead of being mixed into the root guide.

## Theme 3: Agent-Readable Context

This repo is designed so a coding agent can act with less ambiguity.

`AGENTS.md` gives the agent explicit rules:

- Keep changes scoped to the requested task.
- Do not introduce tooling or directory structure unless needed.
- Put design documents under `docs/design/`.
- Use dated design document filenames.
- Update module documentation when changing a module.
- Update `artifacts/README.md` when changing checked-in artifacts.

These instructions reduce repeated prompting. Instead of telling the agent every time where to put files or how to document changes, the repo carries those rules.

The result is a better working loop:

- Human asks for a change.
- Agent reads repository instructions.
- Agent places code and documentation in predictable locations.
- Human reviews both implementation and context updates in the same repo.

## Example Flow

A backend feature in this repo can follow this path:

1. Add or update a design document in `docs/design/`.
2. Implement runtime code under `src/backend/`.
3. Add tests under `tests/`.
4. Update `src/backend/README.md` with module-specific commands or API notes.
5. Keep root docs focused on repository-wide rules only.

This creates a durable context trail: intent, implementation, tests, and local usage notes are all discoverable from the repository tree.

## Why This Helps Teams

Repository context engineering helps with common collaboration problems:

- Reduces repeated explanations across team members and agents.
- Keeps design decisions close to code.
- Makes review easier because context changes are versioned.
- Makes onboarding faster because the tree has clear destinations.
- Makes agent output more consistent because instructions are explicit.

The practical rule is simple: if a future teammate or agent needs the context to make a correct change, put that context in the repo at the narrowest useful scope.

## Adoption Checklist

- Add a root `README.md` for the entry point.
- Add a root `AGENTS.md` for contribution and agent rules.
- Create `docs/design/` for dated design documents.
- Keep module-specific docs beside module code.
- Add `artifacts/README.md` if support artifacts are checked in.
- Keep generated files, dependency folders, and local secrets out of version control.
- Review documentation changes together with code changes.

## Recommended Rule of Thumb

Use the smallest documentation surface that will remain useful:

- Root docs for repository-wide rules.
- Module docs for module-local APIs, commands, and tests.
- Design docs for decisions and tradeoffs.
- Artifact docs for checked-in files that are not runtime source.
- Agent instructions for repeatable rules that agents should follow every time.

