# WhatsApp Agent API Documentation

## Overview

The WhatsApp Agent API allows you to execute automated tasks through WhatsApp, such as booking travel, ordering food, and managing conversations with contacts.

**Base URL**: `http://127.0.0.1:8000` (local development) or your deployed URL

## Core Endpoints

### Execute Task

#### POST `/execute_task`

Execute a WhatsApp task using an AI agent. The agent will process the task, interact with contacts as needed, and report back results.

**Request Body:**
```json
{
  "task": "string",
  "user_id": "string",
  "conversation_id": "string",
  "model": "string",
  "max_iterations": 10,
  "sleep_duration": 30
}
```

**Parameters:**
- `task` (string, required): Description of the task to execute
- `user_id` (string, optional): User ID for context and personalization
- `conversation_id` (string, optional): Conversation ID for context
- `model` (string, optional): LLM model to use (default: "llama-3.3-70b-versatile")
- `max_iterations` (integer, optional): Maximum number of reasoning steps (default: 10)
- `sleep_duration` (integer, optional): Sleep duration in seconds when waiting (default: 30)

**Response:**
```json
{
  "status": "string",
  "message": "string",
  "execution_log": [
    {
      "timestamp": "string",
      "type": "string",
      "message": "string"
    }
  ],
  "task_id": "string",
  "user_id": "string",
  "conversation_id": "string"
}
```

**Example Request:**
```bash
curl --location 'http://127.0.0.1:8000/execute_task' \
--header 'Content-Type: application/json' \
--data '{
  "task": "Ask Alex Choi on +447777777777 when they are available to go to Paris this summer",
  "user_id": "686be51b386780da3a6bbdb5",
  "conversation_id": "686be56af610cdd3b40dbf25"
}'
```

**Example Response:**
```json
{
    "status": "ok",
    "message": "Task started in background",
    "execution_log": [
        {
            "timestamp": "2025-07-07T19:19:38.452421",
            "type": "task_start",
            "message": "Starting task: Ask Alex Choi on +447777777777 when they are available to go to Paris this summer",
            "user_id": "686be51b386780da3a6bbdb5",
            "conversation_id": "686be56af610cdd3b40dbf25"
        }
    ],
    "task_id": "task_20250707_191938",
    "user_id": "686be51b386780da3a6bbdb5",
    "conversation_id": "686be56af610cdd3b40dbf25"
}
```

### Additional Endpoints

#### GET `/health`

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET `/tools`

Get a list of available WhatsApp and Global tools that the agent can use.

**Response:**
```json
{
  "whatsapp_tools": [
    {
      "name": "list_messages",
      "description": "Get messages with filters and context",
      "args_schema": {...}
    },
    // More WhatsApp tools
  ],
  "global_tools": [
    {
      "name": "web_search",
      "description": "Search the web using Tavily API for current information",
      "args_schema": {...}
    },
    // More global tools
  ],
  "total_tools": 20
}
```

#### GET `/models`

Get a list of available LLM models that can be used with the agent.

**Response:**
```json
{
  "models": [
    {
      "name": "llama-3.3-70b-versatile",
      "description": "Llama 3.3 70B - Most capable model, good for complex tasks"
    },
    {
      "name": "llama-3.1-70b-versatile",
      "description": "Llama 3.1 70B - High performance model"
    },
    {
      "name": "llama-3.1-8b-instant",
      "description": "Llama 3.1 8B - Fast and efficient for simple tasks"
    },
    {
      "name": "mixtral-8x7b-32768",
      "description": "Mixtral 8x7B - Good balance of speed and capability"
    },
    {
      "name": "gemma2-9b-it",
      "description": "Gemma 2 9B - Google's efficient model"
    }
  ]
}
```

#### GET `/auto_fetch_status`

Check if the auto-fetch background task for messages is running.

**Response:**
```json
{
  "running": true,
  "message": "Auto-fetch is running"
}
```

## Environment Setup

### Required Environment Variables

```bash
# API Configuration
PORT=8000

# MongoDB Connection
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/whatsapp_agent

# LLM API Keys
GROQ_API_KEY=your_groq_api_key

# Global Tools API
GLOBAL_TOOLS_API_URL=https://global-tools-api-534113739138.europe-west1.run.app
```

## Error Handling

The API returns structured error responses:

```json
{
  "status": "failed",
  "message": "Error executing task: Agent not initialized",
  "execution_log": [
    {
      "timestamp": "2023-07-15T14:30:00.123456",
      "type": "error",
      "message": "API error: Agent not initialized"
    }
  ]
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error (agent initialization failure, etc.)
