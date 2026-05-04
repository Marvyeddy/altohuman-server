# Altohuman Backend

Altohuman Backend is the Python API service for Altohuman. It is built with
FastAPI, SQLModel, and PostgreSQL, with session-aware user lookup designed to
work with Better Auth session cookies.

## Tech Stack

- **FastAPI** for the HTTP API layer
- **SQLModel / SQLAlchemy** for database models and queries
- **PostgreSQL** as the primary database
- **psycopg** for PostgreSQL connectivity
- **uv** for dependency and environment management
- **Python 3.13**

## Project Structure

```text
.
|-- core/
|   |-- config.py        # Environment-based application settings
|   `-- db.py            # Async database session setup
|-- dependencies/
|   `-- user.py          # Current-user dependency from session cookie
|-- error/
|   `-- __init__.py      # Custom application exceptions and handlers
|-- middleware/
|   `-- __init__.py      # Logging, CORS, and trusted host middleware
|-- models/
|   |-- session_model.py # Better Auth-compatible session table
|   `-- user_model.py    # Better Auth-compatible user table
|-- main.py              # FastAPI app entry point
|-- pyproject.toml       # Project metadata and dependencies
`-- uv.lock              # Locked dependency versions
```

## Requirements

- Python `3.13+`
- PostgreSQL
- `uv`

Install `uv` if you do not already have it:

```bash
pip install uv
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Example for local development:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/altohuman
```

## Getting Started

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
uv run fastapi dev main.py
```

The API documentation will be available at:

```text
http://localhost:8000/api/v1/docs
```

ReDoc documentation will be available at:

```text
http://localhost:8000/api/v1/redoc
```

## Authentication Flow

The backend expects authenticated requests to include a Better Auth session
cookie named:

```text
better-auth.session_token
```

The `get_current_user` dependency:

1. Reads the session token from the request cookie.
2. Looks up the token in the `session` table.
3. Checks whether the session has expired.
4. Loads and returns the matching user from the `user` table.

If the cookie is missing, invalid, expired, or points to a missing user, the
dependency raises a custom Altohuman exception.

## Database Models

The current schema includes:

- `user`
  - `id`
  - `name`
  - `email`
  - `createdAt`
  - `updatedAt`
- `session`
  - `id`
  - `userId`
  - `token`
  - `expiresAt`
  - `createdAt`
  - `updatedAt`

The table names and field names are intentionally compatible with Better Auth.

## Middleware

The application configures:

- Request logging with method, path, status code, and processing time
- CORS for `http://localhost:3000`
- Trusted hosts for `localhost` and `127.0.0.1`

## Development Notes

- The API version is currently `v1`.
- Swagger docs are served from `/api/v1/docs`.
- ReDoc is served from `/api/v1/redoc`.
- Custom error handlers are defined in `error/`; wire them into `main.py` with
`require_error(app)` when global exception handling is needed.
- The project currently does not include migrations or route modules.

## Useful Commands

Run the app:

```bash
uv run fastapi dev main.py
```

Install or update dependencies:

```bash
uv sync
```

Add a dependency:

```bash
uv add package-name
```

## License

No license has been specified yet.