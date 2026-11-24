# CUGA runtime for this project. Needed because torch>=2.13 (required by cuga)
# has no Intel-macOS wheels. The project folder is mounted at /app at runtime;
# the virtualenv lives at /opt/venv so it never collides with a host .venv.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

CMD ["uv", "run", "--no-sync", "--env-file", ".env", "python", "llm_smoke.py"]
