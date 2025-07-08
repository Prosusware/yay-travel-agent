# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **SerpApi MCP Server** - an HTTP-based Model Context Protocol server that provides search functionality through SerpApi. The server enables AI assistants to perform web searches, access travel information, hotel data, and more.

**Key Architecture Points:**
- HTTP-based MCP server (not stdio-based) built with FastMCP
- Deployed on Google Cloud Run at: `https://serp-mcp-534113739138.europe-west1.run.app/mcp/`
- Uses `mcp-remote` Node.js package as transport adapter for MCP clients
- Communication flow: `Claude Desktop ←→ stdio ←→ mcp-remote ←→ HTTP ←→ Python MCP Server`

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Create environment file
cp env.yaml.example .env
# Then edit .env to add: SERPAPI_API_KEY=your_key_here
```

### Local Development
```bash
# Run server locally
uv run server.py

# Run with activated virtual environment
source .venv/bin/activate
python server.py
```

### Testing
```bash
# Test the deployed server
python test_mcp.py

# Test server is responding
curl -H "Accept: text/event-stream" "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"

# Test with MCP CLI
npx @modelcontextprotocol/cli@latest http https://serp-mcp-534113739138.europe-west1.run.app/mcp/

# Test transport adapter
npx mcp-remote https://serp-mcp-534113739138.europe-west1.run.app/mcp/
```

### Production Deployment
```bash
# Deploy to Google Cloud Run
gcloud builds submit --config cloudbuild.yaml

# Manual Docker deployment
docker build -t serp-mcp .
docker run -p 8080:8080 --env-file .env serp-mcp
```

## Code Architecture

### Core Components

**server.py** - Main MCP server implementation:
- FastMCP server with two tools: `search()` and `flights()`
- `search()`: General web search using SerpApi (default: google_light engine)
- `flights()`: Flight search using Google Flights API
- Error handling for rate limits, authentication, and network issues

**Key Dependencies:**
- `fastmcp>=2.10.2` - MCP server framework
- `google-search-results>=2.4.2` - SerpApi client
- `httpx>=0.24.0` - HTTP client
- `mcp[cli]>=1.3.0` - MCP protocol support

### Configuration
- Requires `SERPAPI_API_KEY` environment variable
- Default port: 8080
- Deployment uses `env.yaml` for environment variables

### Client Configuration
For Claude Desktop, use this config in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "serp-search": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"]
    }
  }
}
```

## Important Notes

- This is an HTTP-based MCP server, not stdio-based
- Always use `mcp-remote` for client connections (not `@modelcontextprotocol/server-fetch`)
- The server uses `google_light` engine by default for fastest performance
- Error handling includes specific responses for rate limits (429) and auth errors (401)
- Production endpoint is already deployed and accessible