# Hugging Face Docker Space for the Policy Playground tutorial.
# Model settings come from Space secrets: OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/

# Hugging Face runs the container as user 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    UV_PROJECT_ENVIRONMENT=/home/user/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGENT_SETTING_CONFIG=settings.openai.toml \
    CUGA_DBS_DIR=/home/user/dbs \
    CUGA_LOGGING_DIR=/home/user/logs \
    DYNACONF_ADVANCED_FEATURES__TRACKER_ENABLED=false \
    PORT=7860
WORKDIR /home/user/app

COPY --chown=user pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project
COPY --chown=user playground playground

EXPOSE 7860
CMD ["/home/user/venv/bin/python", "playground/web.py"]
