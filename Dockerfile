# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: dependency installer
# Uses the official uv image to resolve and install deps into /app/.venv
# keeping the final image free of uv itself.
# ---------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable uv's Docker optimisations:
#   UV_COMPILE_BYTECODE  — pre-compiles .py → .pyc at build time (faster cold starts)
#   UV_LINK_MODE=copy    — copies packages instead of symlinking (safe across image layers)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install production dependencies only, using the locked versions.
# Mounting the cache avoids re-downloading packages on every rebuild.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

# Copy the application source and install the project itself (no deps re-resolved).
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ---------------------------------------------------------------------------
# Stage 2: runtime image
# Slim image with no build tools, no uv, no root process.
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Create a non-root user to run the process.
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

# Copy only the installed venv and app source from the builder — nothing else.
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app /app

# Put the venv on PATH so `python` and `uvicorn` resolve without activation.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Graceful shutdown: uvicorn handles SIGTERM cleanly.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
