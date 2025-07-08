# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: pull in uv (and uvx) from Astral's slim image
# ──────────────────────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS uv-binaries

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: build Go application with CGO support
# ──────────────────────────────────────────────────────────────────────────────
FROM golang:1.23-alpine AS go-builder

# Install build dependencies for CGO and SQLite
RUN apk add --no-cache gcc musl-dev sqlite-dev

WORKDIR /app

# Copy source code first
COPY whatsapp-mcp/whatsapp-bridge/ .

# Temporarily modify go.mod to use Go 1.23 instead of 1.24.1
RUN sed -i 's/go 1.24.1/go 1.23/' go.mod

# Download dependencies
RUN go mod download

# Build the Go application with CGO enabled
ENV CGO_ENABLED=1
RUN go build -a -ldflags '-linkmode external -extldflags "-static"' -o whatsapp-bridge .

# ──────────────────────────────────────────────────────────────────────────────
# Stage 3: build our final application image with both Python and Go
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

# Install dependencies for both apps
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    ca-certificates \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binaries from first stage
COPY --from=uv-binaries /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# Copy the compiled Go binary from builder stage
COPY --from=go-builder /app/whatsapp-bridge /usr/local/bin/whatsapp-bridge

# Set the working directory to /app
WORKDIR /app

# Copy only the lockfiles (for caching)
COPY pyproject.toml ./

# Use uv to create a `.venv`
RUN uv sync

# Copy the rest of your application code
COPY . .

# Create directory for WhatsApp bridge data
RUN mkdir -p /app/whatsapp-mcp/whatsapp-bridge/store && \
    chmod 755 /app/whatsapp-mcp/whatsapp-bridge/store

# Create supervisor configuration file
RUN mkdir -p /etc/supervisor/conf.d
RUN echo "[supervisord]" > /etc/supervisor/conf.d/supervisord.conf && \
    echo "nodaemon=true" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "user=root" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "[program:python-app]" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "command=uv run uvicorn main:app --host 0.0.0.0 --port 8080" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "directory=/app" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stdout_logfile=/dev/stdout" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stdout_logfile_maxbytes=0" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stderr_logfile=/dev/stderr" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stderr_logfile_maxbytes=0" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "[program:whatsapp-bridge]" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "command=/usr/local/bin/whatsapp-bridge" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "directory=/app/whatsapp-mcp/whatsapp-bridge" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "environment=PORT=8081" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stdout_logfile=/dev/stdout" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stdout_logfile_maxbytes=0" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stderr_logfile=/dev/stderr" >> /etc/supervisor/conf.d/supervisord.conf && \
    echo "stderr_logfile_maxbytes=0" >> /etc/supervisor/conf.d/supervisord.conf

# Tell Cloud Run which port to expect
ENV PORT=8080

# Start supervisor to manage both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]