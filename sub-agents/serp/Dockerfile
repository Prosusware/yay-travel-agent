# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: pull in uv (and uvx) from Astral’s slim image
# ──────────────────────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS uv-binaries

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: build our actual application image
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.13-slim AS final

# 1. Copy both /usr/local/bin/uv and /usr/local/bin/uvx (so uv & uvx are on PATH)
COPY --from=uv-binaries /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# 2. Set the working directory to /app
WORKDIR /app

# 3. Copy only the lockfiles (for caching).
COPY   pyproject.toml   ./

# 4. Use uv to create a `.venv`
RUN uv sync

# 5. Copy the rest of your application code (FastAPI app, etc.)
COPY . .

# 6. Prepend the venv’s bin directory so that "uv", "uvicorn", etc. resolve correctly
ENV PATH="/app/.venv/bin:$PATH"

# 7. Tell Cloud Run which port to expect
ENV PORT=8080
EXPOSE 8080

# 8. Default command: run Uvicorn via uv (inside the venv)
CMD ["uv", "run", "server.py"]
