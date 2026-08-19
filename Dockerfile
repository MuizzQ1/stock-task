FROM python:3.14-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY aapl_stock/ ./aapl_stock/
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8080
EXPOSE 8080

CMD exec fastapi run aapl_stock/api.py --port ${PORT}