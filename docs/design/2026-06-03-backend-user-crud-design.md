# Backend User CRUD Design

- Owner: Codex
- Create Date: 2026-06-03
- Update Date: 2026-06-03

## Overview

This document describes the planned Python backend module for user CRUD APIs. The backend will use FastAPI for HTTP routing, SQLAlchemy for SQLite persistence, and Pydantic schemas for request and response validation.

## Goals

- Provide persistent CRUD APIs for users.
- Store each user with `id`, `name`, `age`, and `job`.
- Generate user IDs on the server as integers.
- Keep the first implementation small, testable, and easy to run locally.

## Non-Goals

- Authentication or authorization.
- Frontend implementation.
- Production migration tooling.
- Role, permission, or organization models.
- Support for databases other than SQLite.

## Architecture

The backend will live under `src/backend/` and expose a FastAPI application. Route handlers will call a small database layer built on SQLAlchemy sessions. Pydantic schemas will define create, update, and response payloads.

Tests will use pytest and FastAPI `TestClient`. Test cases will run against a temporary SQLite database so local development data is not modified.

## API Design

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/users` | Create a user. |
| `GET` | `/api/users` | List users. |
| `GET` | `/api/users/{id}` | Get one user by ID. |
| `PUT` | `/api/users/{id}` | Replace one user. |
| `DELETE` | `/api/users/{id}` | Delete one user. |

### Create User

`POST /api/users`

Request:

```json
{
  "name": "Ada Lovelace",
  "age": 36,
  "job": "Mathematician"
}
```

Response:

```json
{
  "id": 1,
  "name": "Ada Lovelace",
  "age": 36,
  "job": "Mathematician"
}
```

### Validation and Errors

- `name` is required and must be non-empty.
- `age` is required and must be an integer greater than or equal to `0`.
- `job` is required and must be non-empty.
- Missing users return `404`.
- Invalid request bodies return FastAPI validation errors.
- Successful deletes return `204 No Content`.

## Data Model

Table: `users`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | Integer | Primary key, server-generated. |
| `name` | String | Required, non-empty at API validation layer. |
| `age` | Integer | Required, must be `>= 0` at API validation layer. |
| `job` | String | Required, non-empty at API validation layer. |

## Configuration

The backend will read `DATABASE_URL` when provided. If it is not set, it will default to a local SQLite database at `./app.db`.

For the initial scaffold, tables will be created automatically on application startup. Formal migration tooling is deferred until the schema becomes more complex.

## Testing

Use pytest with FastAPI `TestClient`.

Required test scenarios:

- Create a user.
- List users.
- Get a user by ID.
- Update a user.
- Delete a user.
- Return `404` for missing get, update, and delete operations.
- Return validation errors for invalid input.

Tests should use a temporary SQLite database and must not modify `./app.db`.

## Open Notes

- Add migration tooling later if schema changes become frequent.
- Add production database support only when deployment requirements are known.
- Add authentication only when user ownership or protected operations are required.
