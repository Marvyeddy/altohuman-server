# FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     UV_COMPILE_BYTECODE=1 \
#     UV_LINK_MODE=copy

# WORKDIR /app

# RUN groupadd --system app && \
#     useradd --system --gid app --home-dir /app app

# COPY pyproject.toml uv.lock ./

# RUN uv sync --frozen --no-dev --no-install-project

# COPY . .

# RUN uv sync --frozen --no-dev && \
#     chown -R app:app /app

# USER app

# ENV PATH="/app/.venv/bin:$PATH"

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]