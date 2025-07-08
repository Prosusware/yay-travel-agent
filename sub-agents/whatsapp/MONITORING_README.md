# WhatsApp Message Monitoring Feature

This document describes the automatic message monitoring and response feature added to the WhatsApp Agent API.

## Overview

The monitoring feature allows the WhatsApp agent to continuously check for new incoming messages and automatically respond to them using AI. This enables the agent to act as an always-on assistant that can help with travel bookings, food ordering, and general assistance.

## Features

- **Automatic Message Detection**: Checks for new messages at configurable intervals
- **Smart Filtering**: Can ignore own messages, group messages, or empty messages
- **AI-Powered Responses**: Uses the configured LLM to generate contextual responses
- **Comprehensive Logging**: Tracks all monitoring activities with detailed logs
- **Configurable Behavior**: Customize response context, check intervals, and filtering rules

## API Endpoints

### Start Monitoring
```http
POST /start_monitoring
Content-Type: application/json

{
    "check_interval_minutes": 1,
    "auto_respond": true,
    "response_context": "You are Prosusware, a helpful assistant...",
    "ignore_own_messages": true,
    "only_respond_to_direct_messages": true
}
```

### Stop Monitoring
```http
POST /stop_monitoring
```

### Get Monitoring Status
```http
GET /monitoring_status
```

Response:
```json
{
    "enabled": true,
    "last_check_time": "2024-01-15T10:30:00",
    "next_check_in_seconds": 45,
    "processed_messages_count": 12
}
```

### Get Monitoring Logs
```http
GET /monitoring_logs?limit=50
```

### Clear Monitoring Logs
```http
POST /clear_monitoring_logs
```

### Update Monitoring Configuration
```http
POST /update_monitoring_config
Content-Type: application/json

{
    "check_interval_minutes": 2,
    "auto_respond": false
}
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `check_interval_minutes` | int | 1 | How often to check for new messages |
| `auto_respond` | bool | true | Whether to automatically respond to messages |
| `response_context` | string | "You are Prosusware..." | Context for AI responses |
| `ignore_own_messages` | bool | true | Skip messages sent by the agent |
| `only_respond_to_direct_messages` | bool | true | Skip group messages |

## Usage Examples

### Basic Usage

1. **Start the server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Start monitoring**:
   ```bash
   curl -X POST http://localhost:8000/start_monitoring \
        -H "Content-Type: application/json" \
        -d '{"check_interval_minutes": 1, "auto_respond": true}'
   ```

3. **Check status**:
   ```bash
   curl http://localhost:8000/monitoring_status
   ```

4. **View logs**:
   ```bash
   curl http://localhost:8000/monitoring_logs
   ```

5. **Stop monitoring**:
   ```bash
   curl -X POST http://localhost:8000/stop_monitoring
   ```

### Using the Test Script

Run the included test script to see the monitoring in action:

```bash
python test_monitoring.py
```

This script will:
- Start monitoring with a custom configuration
- Monitor for 3 minutes while showing status updates
- Display recent logs
- Stop monitoring
- Show final statistics

## How It Works

1. **Initialization**: When monitoring starts, the system records the current timestamp
2. **Periodic Checks**: Every N minutes (configurable), the system:
   - Queries for messages newer than the last check time
   - Filters messages based on configuration
   - Processes each new message
3. **Message Processing**: For each new message:
   - Extracts sender, content, and chat information
   - Checks if the message should be processed (not own message, not group if configured, etc.)
   - Marks the message as processed to avoid duplicates
4. **AI Response**: If auto-respond is enabled:
   - Creates a task for the AI agent with the message content and context
   - The agent generates an appropriate response
   - Sends the response back to the sender

## Logging

The system maintains detailed logs of all monitoring activities:

- **INFO**: Important events (monitoring started/stopped, messages found)
- **DEBUG**: Detailed information (message checks, skipped messages)
- **SUCCESS**: Successful operations (responses sent)
- **ERROR**: Error conditions (API failures, processing errors)

## Error Handling

The monitoring system is designed to be resilient:

- **Network Errors**: Continues monitoring after temporary network issues
- **API Errors**: Logs errors and continues checking for new messages
- **Processing Errors**: Individual message processing errors don't stop the monitoring loop
- **Rate Limiting**: Respects the configured check interval to avoid overwhelming the system

## Performance Considerations

- **Memory Usage**: Processed message IDs are stored in memory to avoid duplicates
- **Log Rotation**: Monitoring logs are automatically limited to the last 1000 entries
- **Async Operations**: All operations are asynchronous to avoid blocking
- **Batch Processing**: Checks up to 50 messages per cycle for efficiency

## Security Notes

- The monitoring feature only processes messages that the WhatsApp bridge has access to
- All responses are generated through the same AI agent with the same safety constraints
- Monitoring can be stopped at any time
- Logs contain message previews but full message content is not permanently stored

## Troubleshooting

### Common Issues

1. **Monitoring not starting**: Ensure the WhatsApp bridge is connected and the agent is initialized
2. **No responses being sent**: Check that `auto_respond` is `true` and the AI model is working
3. **Duplicate responses**: The system should prevent this, but check logs for any processing errors
4. **Missing messages**: Verify the WhatsApp bridge is receiving messages correctly

### Debug Steps

1. Check monitoring status: `GET /monitoring_status`
2. Review logs: `GET /monitoring_logs`
3. Test manual message sending: `POST /execute_task`
4. Verify WhatsApp tools: `GET /tools`

## Example Integration

```python
import requests
import time

# Configure monitoring for travel booking assistance
config = {
    "check_interval_minutes": 1,
    "auto_respond": True,
    "response_context": """You are Prosusware, a travel booking assistant. 
    Help users with:
    - Flight bookings
    - Hotel reservations  
    - Restaurant recommendations
    - Travel planning
    
    Be helpful, professional, and ask clarifying questions when needed.""",
    "ignore_own_messages": True,
    "only_respond_to_direct_messages": True
}

# Start monitoring
response = requests.post("http://localhost:8000/start_monitoring", json=config)
print("Monitoring started:", response.json())

# Monitor and log activity
while True:
    time.sleep(60)  # Check every minute
    
    status = requests.get("http://localhost:8000/monitoring_status").json()
    print(f"Processed {status['processed_messages_count']} messages")
    
    # Get recent logs
    logs = requests.get("http://localhost:8000/monitoring_logs?limit=5").json()
    for log in logs['logs'][-3:]:
        print(f"[{log['type']}] {log['message']}")
```

This monitoring feature transforms the WhatsApp agent from a manual tool into an always-on assistant that can provide immediate help to users. 