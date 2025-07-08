# Quick Start Guide - WhatsApp LangGraph Agent (Groq Edition)

## 🚀 Get Started in 5 Minutes

### 1. Set Up Environment Variables

Create a `.env` file in your project root:

```bash
# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: https://console.groq.com/keys

### 2. Install Dependencies

```bash
pip install -e .
# or with uv:
uv sync
```

### 3. Start WhatsApp Bridge

In a separate terminal:

```bash
cd whatsapp-mcp/whatsapp-bridge
go run main.go
```

*Note: You'll need to scan the QR code with your WhatsApp mobile app the first time.*

### 4. Start the Agent API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Test the Agent

```bash
python test_agent.py
```

## 📱 Quick Examples

### Send a Message

```bash
curl -X POST "http://localhost:8000/execute_task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Send a message to John saying Hello!",
    "model": "llama-3.3-70b-versatile"
  }'
```

### Search Contacts

```bash
curl -X POST "http://localhost:8000/execute_task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Find all contacts named Sarah",
    "model": "llama-3.1-8b-instant"
  }'
```

### Get Recent Messages

```bash
curl -X POST "http://localhost:8000/execute_task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Show me the last 10 messages from my most active chat",
    "model": "mixtral-8x7b-32768"
  }'
```

## 🎯 What You Can Do

- **📨 Send Messages**: "Send a message to John saying 'Meeting at 3pm'"
- **🔍 Search Contacts**: "Find all contacts with phone numbers starting with +1"
- **📋 List Chats**: "Show me all my group chats"
- **📥 Download Media**: "Download the latest image from my chat with Alice"
- **🤖 Complex Tasks**: "Check recent messages for anyone asking about deadlines and reply with the project timeline"

## 🛠️ Available Groq Models

- **`llama-3.3-70b-versatile`** (default) - Most capable model, best for complex tasks
- **`llama-3.1-70b-versatile`** - High performance model
- **`llama-3.1-8b-instant`** - Fast and efficient for simple tasks
- **`mixtral-8x7b-32768`** - Good balance of speed and capability
- **`gemma2-9b-it`** - Google's efficient model

## 📊 Response Format

```json
{
  "status": "ok",  // "ok" or "failed"
  "message": "Task completed successfully",
  "execution_log": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "type": "task_start",
      "message": "Starting task..."
    }
  ],
  "task_id": "task_20240115_103000"
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Agent not initialized"**: Wait a few seconds after starting the API
2. **"Contact not found"**: Make sure the contact exists in your WhatsApp
3. **"Connection error"**: Check if the WhatsApp bridge is running
4. **"API key error"**: Verify your GROQ_API_KEY in `.env`

### Health Check

```bash
curl http://localhost:8000/health
```

Should return: `{"status": "healthy"}`

### Available Models

```bash
curl http://localhost:8000/models
```

Lists all available Groq models with descriptions.

## 🎉 What's Next?

1. Explore the `/models` endpoint to see all available Groq models
2. Try different models for different task complexities
3. Experiment with complex multi-step tasks
4. Integrate with your own applications using the REST API

## 💡 Pro Tips

- Use **llama-3.3-70b-versatile** for complex reasoning tasks
- Use **llama-3.1-8b-instant** for simple, fast operations
- Use **mixtral-8x7b-32768** for balanced performance
- Be specific with contact names to avoid ambiguity
- Check the execution log to debug issues
- Set higher `max_iterations` for complex tasks

## 🚀 Why Groq?

- **Lightning Fast**: Groq's LPU™ inference is incredibly fast
- **Cost Effective**: Competitive pricing with generous free tiers
- **High Quality**: Latest open-source models like Llama 3.3
- **Reliable**: Enterprise-grade infrastructure 