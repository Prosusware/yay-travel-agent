# WhatsApp LangGraph Agent API

This API provides a LangGraph-powered agent that can execute WhatsApp tasks using natural language commands. The agent can search contacts, read messages, send messages, handle media, and perform complex WhatsApp automation tasks.

## Features

- **Natural Language Task Processing**: Describe what you want to do in plain English
- **Multiple LLM Support**: Works with OpenAI GPT models and Anthropic Claude models
- **Comprehensive WhatsApp Tools**: Access to all WhatsApp MCP server capabilities
- **Detailed Execution Logs**: Track every step of task execution
- **Error Handling**: Graceful error handling with informative messages

## Setup

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# Groq API Key
GROQ_API_KEY=<string>
```

### 2. Prerequisites

Make sure you have the WhatsApp MCP server running:

1. **Start the WhatsApp bridge** (in a separate terminal):
   ```bash
   cd whatsapp-mcp/whatsapp-bridge
   go run main.go
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or if using uv:
   uv sync
   ```

### 3. Run the Agent API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/execute_task`

Execute a WhatsApp task using natural language.

**Request Body:**
```json
{
  "task": "Send a message to John saying 'Hello, how are you?'",
  "model": "gpt-4o-mini",
  "max_iterations": 10
}
```

**Parameters:**
- `task` (required): Natural language description of what you want to do
- `model` (optional): AI model to use (`gpt-4o-mini`, `gpt-4o`, `claude-3-5-sonnet-20241022`, etc.)
- `max_iterations` (optional): Maximum number of reasoning iterations (default: 10)

**Response:**
```json
{
  "status": "ok",
  "message": "Task completed successfully",
  "execution_log": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "type": "task_start",
      "message": "Starting task: Send a message to John saying 'Hello, how are you?'"
    },
    {
      "timestamp": "2024-01-15T10:30:01",
      "type": "reasoning",
      "message": "I need to search for John's contact first, then send the message.",
      "iteration": 1
    },
    {
      "timestamp": "2024-01-15T10:30:02",
      "type": "tool_call",
      "tool_name": "search_contacts",
      "args": {"query": "John"},
      "iteration": 1
    },
    {
      "timestamp": "2024-01-15T10:30:03",
      "type": "tool_result",
      "tool_name": "search_contacts",
      "result": [{"name": "John Smith", "phone_number": "1234567890", "jid": "1234567890@s.whatsapp.net"}],
      "iteration": 1
    }
  ],
  "task_id": "task_20240115_103000"
}
```

### GET `/tools`

Get a list of available WhatsApp tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "search_contacts",
      "description": "Search WhatsApp contacts by name or phone number",
      "args_schema": { ... }
    },
    ...
  ]
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Example Tasks

Here are some example tasks you can execute:

### Basic Messaging
```json
{
  "task": "Send a message to John saying 'Hello, how are you?'"
}
```

### Contact Management
```json
{
  "task": "Find all contacts named Sarah and show me their phone numbers"
}
```

### Message Analysis
```json
{
  "task": "Find all messages from Alice in the last week and summarize what she talked about"
}
```

### Media Handling
```json
{
  "task": "Download the latest image from my chat with Bob"
}
```

### Group Operations
```json
{
  "task": "Send a message to the 'Project Team' group asking about the meeting time"
}
```

### Complex Automation
```json
{
  "task": "Check my recent messages, find anyone who asked about the project deadline, and reply with 'The deadline is next Friday'"
}
```

## Available WhatsApp Tools

The agent has access to these WhatsApp tools:

1. **search_contacts**: Search for contacts by name or phone number
2. **list_messages**: Get messages with filters and context
3. **list_chats**: List available chats
4. **get_chat**: Get chat information by JID
5. **get_direct_chat_by_contact**: Find direct chat with a contact
6. **get_contact_chats**: List all chats involving a contact
7. **get_last_interaction**: Get most recent message with a contact
8. **get_message_context**: Get context around a specific message
9. **send_message**: Send a message to a contact or group
10. **send_file**: Send a file (image, video, document)
11. **send_audio_message**: Send an audio message
12. **download_media**: Download media from a message

## Agent Behavior

The agent follows these principles:

1. **Safety First**: Always searches for contacts before sending messages
2. **Context Awareness**: Gathers relevant information before taking actions
3. **Error Handling**: Gracefully handles errors and provides feedback
4. **Iteration Limits**: Respects maximum iteration limits to prevent infinite loops
5. **Detailed Logging**: Provides comprehensive execution logs

## Error Handling

The agent handles various error scenarios:

- **Contact Not Found**: Will search for similar contacts and ask for clarification
- **Message Send Failures**: Will retry with different approaches
- **API Errors**: Will provide detailed error messages
- **Tool Execution Errors**: Will attempt alternative approaches

## Response Status

- **"ok"**: Task completed successfully
- **"failed"**: Task failed with error details in the message

## Tips for Better Results

1. **Be Specific**: "Send a message to John Smith" is better than "Send a message to John"
2. **Provide Context**: Include relevant details like time ranges, message content, etc.
3. **Use Natural Language**: The agent understands conversational instructions
4. **Handle Ambiguity**: If there are multiple contacts with the same name, the agent will ask for clarification

## Troubleshooting

### Common Issues

1. **Agent Not Responding**: Check if the WhatsApp bridge is running
2. **Contact Not Found**: Verify the contact exists in your WhatsApp
3. **Message Send Failures**: Ensure the recipient is using WhatsApp
4. **API Key Errors**: Verify your Groq API keys are correct

### Debugging

Use the execution log to understand what the agent is doing:

```python
import requests

response = requests.post("http://localhost:8000/execute_task", json={
    "task": "Your task here"
})

# Check the execution log
for log_entry in response.json()["execution_log"]:
    print(f"{log_entry['timestamp']}: {log_entry['type']} - {log_entry['message']}")
```

## License

This project uses the same license as the original WhatsApp MCP server. 