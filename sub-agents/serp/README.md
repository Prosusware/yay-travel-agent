# SerpApi MCP Server

A Model Context Protocol (MCP) server that provides search functionality through SerpApi. This server enables AI assistants to perform web searches, access travel information, hotel data, maps, and more through SerpApi's comprehensive search engines.

## Features

- **Web Search**: Google search results with organic results
- **Fast Performance**: Uses Google Light engine by default for optimal speed
- **Flexible Parameters**: Support for location-based searches and engine-specific parameters
- **Error Handling**: Comprehensive error handling for rate limits, authentication, and network issues
- **Production Ready**: Containerized and deployable to cloud platforms
- **HTTP-Based**: Built with FastMCP for easy deployment and scaling

## Architecture

This is an **HTTP-based MCP server** (not stdio-based), which means:
- ✅ Easy to deploy to cloud platforms
- ✅ Can handle multiple concurrent requests
- ✅ Scalable and stateless
- ✅ Works behind load balancers

**MCP Client Connection Flow:**
```
Claude Desktop ←→ stdio ←→ mcp-remote ←→ HTTP ←→ Python MCP Server
```

The `mcp-remote` package bridges the communication between stdio-expecting MCP clients and HTTP-based servers.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Usage](#usage)
- [Production Deployment](#production-deployment)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Python 3.13+
- SerpApi API key (get one at [serpapi.com](https://serpapi.com))
- An MCP-compatible client (like Claude Desktop, Cline, or any MCP client)

### Production Usage (Deployed Server)

The server is already deployed and available at:
```
https://serp-mcp-534113739138.europe-west1.run.app/mcp/
```

To use this in your MCP client, add the following configuration:

**For Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "serp-search": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
      ]
    }
  }
}
```

> **Why `npx` for a Python server?** This Python server runs over HTTP using FastMCP, but MCP clients like Claude Desktop communicate via stdio. The `mcp-remote` Node.js package acts as a transport adapter, bridging stdio ↔ HTTP communication.

## Local Development

### 1. Clone and Setup

```bash
git clone <repository-url>
cd serp-mcp
```

### 2. Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 3. Environment Configuration

Create a `.env` file with your SerpApi credentials:

```bash
cp env.yaml.example .env
```

Edit `.env` and add your API key:
```
SERPAPI_API_KEY=your_serpapi_api_key_here
```

### 4. Run Locally

```bash
# Using uv
uv run server.py

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python server.py
```

The server will start on `http://localhost:8080/mcp/`

### 5. Connect to MCP Client

For local development with Claude Desktop, update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "serp-search-local": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8080/mcp/"
      ]
    }
  }
}
```

> **Note:** Even for local development, we use the HTTP transport adapter because this is an HTTP-based MCP server, not a stdio-based one.

## Usage

### Basic Search

The server provides a `search` tool that accepts various parameters:

```python
# Basic search
search({"q": "coffee shops near me"})

# Search with location
search({
    "q": "restaurants",
    "location": "Austin, TX"
})

# Search with specific engine
search({
    "q": "weather",
    "engine": "google",
    "location": "London, UK"
})
```

### Available Parameters

- `q` (string): Search query
- `engine` (string): Search engine (default: "google_light")
- `location` (string): Geographic location for search
- `num` (integer): Number of results to return
- `start` (integer): Starting position for results
- Any other SerpApi-supported parameters

### Response Format

The tool returns formatted search results as a string:

```
Title: Coffee Shop Name
Link: https://example.com
Snippet: Description of the coffee shop...

Title: Another Coffee Shop
Link: https://example2.com
Snippet: Another description...
```

### Example Usage in Claude

Once connected, you can ask Claude to search for information:

- "Search for the latest news about artificial intelligence"
- "Find restaurants in Tokyo, Japan"
- "Look up weather information for San Francisco"
- "Search for hotels in Paris with good reviews"

## Production Deployment

### Google Cloud Run (Current Deployment)

The server is deployed using Google Cloud Build and Cloud Run:

```bash
# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy manually
docker build -t gcr.io/YOUR_PROJECT_ID/serp-mcp:latest .
docker push gcr.io/YOUR_PROJECT_ID/serp-mcp:latest

gcloud run deploy serp-mcp \
  --image gcr.io/YOUR_PROJECT_ID/serp-mcp:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --env-vars-file env.yaml
```

### Environment Variables for Production

Create `env.yaml` for production deployment:

```yaml
SERPAPI_API_KEY: "your_production_api_key"
```

### Other Deployment Options

#### Docker
```bash
docker build -t serp-mcp .
docker run -p 8080:8080 --env-file .env serp-mcp
```

#### Railway, Render, or Heroku
The Dockerfile is compatible with most cloud platforms. Set the `SERPAPI_API_KEY` environment variable in your platform's configuration.

## API Reference

### Tool: `search`

Performs a search using SerpApi.

**Parameters:**
- `params` (Dict[str, Any]): Dictionary of search parameters

**Default Parameters:**
- `engine`: "google_light" (fastest engine)
- `api_key`: Automatically added from environment

**Returns:**
- `str`: Formatted search results or error message

**Supported Engines:**
- `google_light` (default, fastest)
- `google`
- `bing`
- `yahoo`
- `duckduckgo`
- `yandex`
- And many more (see [SerpApi documentation](https://serpapi.com/search-engines))

**Error Handling:**
- Rate limit exceeded (429): Returns rate limit message
- Invalid API key (401): Returns authentication error
- Network issues: Returns generic error message

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SERPAPI_API_KEY` | Yes | Your SerpApi API key | None |
| `PORT` | No | Server port | 8080 |

### SerpApi Configuration

Get your API key from [SerpApi](https://serpapi.com):
1. Create an account
2. Go to your dashboard
3. Copy your API key
4. Add it to your environment configuration

**Free tier includes:**
- 100 searches per month
- Access to all search engines
- Full API features

## Troubleshooting

### Common Issues

**1. "SERPAPI_API_KEY not found in environment variables"**
- Ensure your `.env` file contains the API key
- Check that the environment variable is properly set in production

**2. "Rate limit exceeded"**
- You've exceeded your SerpApi monthly quota
- Upgrade your SerpApi plan or wait for the next billing cycle

**3. "Invalid API key"**
- Double-check your API key from SerpApi dashboard
- Ensure there are no extra spaces or characters

**4. Connection timeout**
- Check your internet connection
- SerpApi service might be temporarily unavailable

**5. MCP client not connecting**
- Verify the server URL is correct
- Check that the server is running and accessible
- Review MCP client configuration syntax
- Ensure you're using `mcp-remote` (not `@modelcontextprotocol/server-fetch`)

**6. "Package not found" error (E404)**
```
npm error 404 Not Found - GET https://registry.npmjs.org/@modelcontextprotocol%2fserver-fetch
```
- This error occurs when using the incorrect package name
- **Solution**: Use `mcp-remote` instead of `@modelcontextprotocol/server-fetch`
- Update your Claude Desktop config to use the correct package name
- Restart Claude Desktop after making the change

### Debug Mode

Run with debug logging:
```bash
# Local development
PYTHONPATH=. python -m uvicorn server:mcp --host 0.0.0.0 --port 8080 --reload --log-level debug
```

### Testing the Server

**1. Test server is responding:**
```bash
curl -H "Accept: text/event-stream" \
  "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
```

**2. Test with MCP CLI:**
```bash
npx @modelcontextprotocol/cli@latest http https://serp-mcp-534113739138.europe-west1.run.app/mcp/
```

**3. Test the transport adapter:**
```bash
# Test that mcp-remote can connect to your server
npx mcp-remote https://serp-mcp-534113739138.europe-west1.run.app/mcp/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

- [SerpApi Documentation](https://serpapi.com/search-api)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

---

**Production Endpoint:** https://serp-mcp-534113739138.europe-west1.run.app/mcp/
