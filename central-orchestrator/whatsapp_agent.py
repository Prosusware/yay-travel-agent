import os
import requests
import json
from typing import Dict, Any, Optional
from utils import tool_wrapper

# Base URL for the WhatsApp Agent API
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "http://127.0.0.1:8000")

@tool_wrapper
def execute_whatsapp_task(
    task: str,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a task using the WhatsApp agent.

    Args:
        task: A detailed description of the task to be executed. It should include the phone number of the person to contact.

    Returns:
        A dictionary with the task execution result.
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string and is injected by the agent")
    if not conversation_id or not isinstance(conversation_id, str):
        raise ValueError("conversation_id must be a non-empty string and is injected by the agent")

    endpoint = f"{WHATSAPP_API_URL}/execute_task"

    model = "llama-3.3-70b-versatile"
    
    payload = {
        "task": task,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "model": model,
        "max_iterations": 10
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Executing WhatsApp task: {task}")
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error executing WhatsApp task: {str(e)}")
        error_response = {"success": False, "error": str(e)}
        if e.response:
            try:
                error_response["details"] = e.response.json()
            except json.JSONDecodeError:
                error_response["details"] = e.response.text
        return error_response 