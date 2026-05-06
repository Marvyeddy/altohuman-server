# Altohuman Backend

Altohuman Backend is the FastAPI service for Altohuman. It provides
session-aware user lookup for Better Auth cookies, credit-based text
humanization/scoring, and Paystack payment handling.

## Tech Stack

- **FastAPI** for the HTTP API layer
- **SQLModel / SQLAlchemy** for database models and queries
- **PostgreSQL** as the primary database
- **asyncpg** for async PostgreSQL connectivity
- **Alembic** for database migrations
- **LangChain Groq** for text scoring and humanization
- **uv** for dependency and environment management
- **Python 3.13+**

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
|-- migrations/          # Alembic migration environment and versions
|-- models/              # SQLModel database models
|-- routes/
|   |-- humanizer_route.py
|   |-- payment_route.py
|   `-- user_route.py
|-- schema/              # API response/request schemas
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
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
PAYSTACK_SECRET_KEY=sk_test_or_live_key
GROQ_API_KEY=your_groq_api_key
```

Example for local development:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/altohuman
PAYSTACK_SECRET_KEY=sk_test_xxx
GROQ_API_KEY=gsk_xxx
```

## Getting Started

Install dependencies:

```bash
uv sync
```

Apply database migrations:

```bash
uv run alembic upgrade head
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

## API Routes

All routes are mounted under `/api/v1`.

- `GET /user/me` returns the authenticated user's profile.
- `POST /humanize/` scores or humanizes text, charging user credits.
- `POST /payment/initialize/{plan_name}` creates a Paystack checkout session.
- `POST /payment/webhook` receives Paystack payment events.

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

The schema includes Better Auth-compatible user, session, account, and
verification tables, plus Altohuman payment and credit fields.

Important user fields include:

- `id`
- `name`
- `email`
- `credit`
- `wordLimit`
- `currentPlan`
- `createdAt`
- `updatedAt`

Payment records store the Paystack reference, amount, granted credits, selected
plan, status, and related user.

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
- Paystack checkout callbacks currently point to
  `http://localhost:3000/dashboard?status=success`.

## Useful Commands

Run the app:

```bash
uv run fastapi dev main.py
```

Run migrations:

```bash
uv run alembic upgrade head
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
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
