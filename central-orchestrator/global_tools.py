import os
import requests
import json
from typing import Dict, Any, Optional, List
from utils import tool_wrapper

# Base URL for the Global Tools API
BASE_URL = os.getenv("GLOBAL_TOOLS_URL", "https://api.your-global-tools.com")

@tool_wrapper
def global_web_search(query: str) -> Dict[str, Any]:
    """
    Search the web using the Global Tools API.
    
    Args:
        query: The search query.
        
    Returns:
        A dictionary containing the search results.
    """
    try:
        response = requests.get(f"{BASE_URL}/api/search", params={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def add_contact(user_id: str, contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new contact for the current user. The user_id is handled automatically by the agent.
    
    Args:
        contact: A dictionary with contact details (e.g., FirstName, LastName, email, phoneNumber).
        
    Returns:
        The result of the operation.
    """
    payload = {"UserID": user_id, "contact": contact}
    try:
        response = requests.post(f"{BASE_URL}/api/contacts/add", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def update_contact(user_id: str, contact_uid: str, contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing contact for the current user. The user_id is handled automatically by the agent.
    
    Args:
        contact_uid: The unique ID of the contact to update.
        contact: A dictionary with the contact fields to update.
        
    Returns:
        The result of the operation.
    """
    payload = {"UserID": user_id, "contact_uid": contact_uid, "contact": contact}
    try:
        response = requests.patch(f"{BASE_URL}/api/contacts/update", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def get_contacts(user_id: str) -> Dict[str, Any]:
    """
    Get all contacts for the current user. The user_id is handled automatically by the agent.
        
    Returns:
        A dictionary containing the user's contacts.
    """
    try:
        response = requests.get(f"{BASE_URL}/api/contacts/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def get_user(user_id: str) -> Dict[str, Any]:
    """
    Get a user object by their ID.

    Args:
        user_id: The MongoDB _id of the user.

    Returns:
        A dictionary containing the user data.
    """
    if not user_id:
        return {"error": "User ID is required"}
    try:
        response = requests.get(f"{BASE_URL}/api/user/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def add_memory(user_id: str, memory: str, contact_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a memory for the current user. The user_id is handled automatically by the agent.
    
    Args:
        memory: The memory text to add.
        contact_id: Optional ID of the contact associated with the memory.
        email: Optional email of the contact associated with the memory.
        
    Returns:
        The result of the operation.
    """
    payload = {"user_id": user_id, "memory": memory}
    if contact_id:
        payload["contact_id"] = contact_id
    if email:
        payload["email"] = email
        
    try:
        response = requests.post(f"{BASE_URL}/api/memory/add", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def search_memory(user_id: str, query: str, n_results: int = 10, search_all_collections: bool = False) -> Dict[str, Any]:
    """
    Search memories for the current user. The user_id is handled automatically by the agent.
    
    Args:
        query: The search query.
        n_results: The number of results to return.
        search_all_collections: Whether to search across all of the user's collections.
        
    Returns:
        A dictionary containing the search results.
    """
    payload = {
        "user_id": user_id,
        "query": query,
        "n_results": n_results,
        "search_all_collections": search_all_collections,
    }
    try:
        response = requests.post(f"{BASE_URL}/api/memory/search", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def write_status(agent_id: str, agent_type: str, conversation_id: str, update: str) -> Dict[str, Any]:
    """
    Write a status update for the current conversation. The conversation_id is handled automatically by the agent.
    
    Args:
        agent_id: The ID of the agent writing the status.
        agent_type: The type of the agent (e.g., 'assistant').
        update: The status update message.
        
    Returns:
        The result of the operation.
    """
    payload = {
        "agent_id": "orchestrator",
        "agent_type": "orchestrator",
        "conversation_id": conversation_id,
        "update": update,
    }
    try:
        response = requests.post(f"{BASE_URL}/api/status/write", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

@tool_wrapper
def read_status(conversation_id: str) -> Dict[str, Any]:
    """
    Read status updates for the current conversation. The conversation_id is handled automatically by the agent.
    
    Args:
        conversation_id: The ID of the conversation.
        
    Returns:
        A dictionary containing the status updates.
    """
    try:
        response = requests.post(f"{BASE_URL}/api/status/read", json={"conversation_id": conversation_id})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error reading status: {str(e)}")
        return {"success": False, "error": str(e)} 