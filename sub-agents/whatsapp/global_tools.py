import os
import requests
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import pymongo
from pymongo import MongoClient
import uuid

# Environment variables
GLOBAL_TOOLS_API_URL = os.environ.get("GLOBAL_TOOLS_API_URL", "https://global-tools-api-534113739138.europe-west1.run.app")
MONGODB_URL = os.environ.get("MONGODB_CONNECTION_STRING")

# MongoDB client for direct access
mongo_client = None
db = None

def init_global_tools_mongodb():
    """Initialize MongoDB connection for global tools"""
    global mongo_client, db
    try:
        if MONGODB_URL:
            mongo_client = MongoClient(MONGODB_URL)
            db = mongo_client["Prosusware"]
            return True
    except Exception as e:
        print(f"Failed to initialize MongoDB for global tools: {e}")
    return False

# Initialize MongoDB on import
init_global_tools_mongodb()

# Pydantic models for request validation
class ContactData(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    nickname: Optional[str] = None
    email: str
    phoneNumber: Optional[str] = None

class AddContactRequest(BaseModel):
    UserID: str
    contact: ContactData

class UpdateContactRequest(BaseModel):
    UserID: str
    contact_uid: str
    contact: Dict[str, Any]

class MemoryAddRequest(BaseModel):
    user_id: str
    memory_text: str
    contact_email: Optional[str] = None

class MemorySearchRequest(BaseModel):
    user_id: str
    query: str
    n_results: Optional[int] = 5

class StatusWriteRequest(BaseModel):
    agent_id: str
    agent_type: str
    conversation_id: str
    update: str

class StatusReadRequest(BaseModel):
    conversation_id: str
    agent_type: Optional[str] = None
    agent_id: Optional[str] = None

class VectorAddRequest(BaseModel):
    collection_name: str
    documents: List[str]
    ids: Optional[List[str]] = None
    metadatas: Optional[List[Dict[str, Any]]] = None

class VectorQueryRequest(BaseModel):
    collection_name: str
    query_texts: List[str]
    n_results: Optional[int] = 5
    where: Optional[Dict[str, Any]] = None
    include: Optional[List[str]] = None

# Service Functions

def tavily_search(query: str) -> Dict[str, Any]:
    """Perform web search using Tavily API"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/search"
        params = {"query": query}
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Search failed with status {response.status_code}",
                "query": query,
                "context": "",
                "source_count": 0
            }
    except Exception as e:
        return {
            "error": f"Search error: {str(e)}",
            "query": query,
            "context": "",
            "source_count": 0
        }

def add_contact(user_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new contact"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/contacts/add"
        data = {
            "UserID": user_id,
            "contact": contact_data
        }
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to add contact: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Contact add error: {str(e)}"}

def update_contact(user_id: str, contact_uid: str, contact_updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing contact"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/contacts/update"
        data = {
            "UserID": user_id,
            "contact_uid": contact_uid,
            "contact": contact_updates
        }
        response = requests.patch(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to update contact: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Contact update error: {str(e)}"}

def get_user_contacts(user_id: str) -> Dict[str, Any]:
    """Get all contacts for a user"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/contacts/{user_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get contacts: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Get contacts error: {str(e)}"}

def add_memory(user_id: str, memory_text: str, contact_email: Optional[str] = None) -> Dict[str, Any]:
    """Add a memory to the vector database"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/memory/add"
        data = {
            "user_id": user_id,
            "memory_text": memory_text
        }
        if contact_email:
            data["contact_email"] = contact_email
            
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to add memory: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Memory add error: {str(e)}"}

def search_memory(user_id: str, query: str, n_results: int = 5) -> Dict[str, Any]:
    """Search memories using natural language"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/memory/search"
        data = {
            "user_id": user_id,
            "query": query,
            "n_results": n_results
        }
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to search memory: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Memory search error: {str(e)}"}

def write_status_update(agent_id: str, agent_type: str, conversation_id: str, update: str) -> Dict[str, Any]:
    """Write a status update"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/status/write"
        data = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "conversation_id": conversation_id,
            "update": update
        }
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to write status: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Status write error: {str(e)}"}

def read_status_updates(conversation_id: str, agent_type: Optional[str] = None, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Read status updates for a conversation"""
    try:
        url = f"{GLOBAL_TOOLS_API_URL}/api/status/read"
        data = {"conversation_id": conversation_id}
        if agent_type:
            data["agent_type"] = agent_type
        if agent_id:
            data["agent_id"] = agent_id
            
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to read status: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Status read error: {str(e)}"}

# Tool Definitions

@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily API for current information.
    
    Args:
        query: The search query string
        
    Returns:
        Formatted search results with context and sources
    """
    result = tavily_search(query)
    
    if "error" in result:
        return f"Search failed: {result['error']}"
    
    context = result.get("context", "")
    source_count = result.get("source_count", 0)
    
    return f"Search Results for '{query}':\n\n{context}\n\nFound {source_count} sources."

@tool
def add_contact_tool(user_id: str, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None, nickname: Optional[str] = None, phone_number: Optional[str] = None) -> str:
    """
    Add a new contact for a user. Only email is required.
    
    Args:
        user_id: The user ID to add the contact for
        email: Contact's email address (required)
        first_name: Contact's first name (optional)
        last_name: Contact's last name (optional)
        nickname: Contact's nickname (optional)
        phone_number: Contact's phone number (optional)
        
    Returns:
        Success message with contact details or error message
    """
    contact_data = {"email": email}
    
    if first_name:
        contact_data["FirstName"] = first_name
    if last_name:
        contact_data["LastName"] = last_name
    if nickname:
        contact_data["nickname"] = nickname
    if phone_number:
        contact_data["phoneNumber"] = phone_number
    
    result = add_contact(user_id, contact_data)
    
    if "error" in result:
        return f"Failed to add contact: {result['error']}"
    
    return f"Contact added successfully: {result.get('message', 'Contact created')}"

@tool
def update_contact_tool(user_id: str, contact_uid: str, first_name: Optional[str] = None, last_name: Optional[str] = None, nickname: Optional[str] = None, phone_number: Optional[str] = None, email: Optional[str] = None) -> str:
    """
    Update an existing contact with new information.
    
    Args:
        user_id: The user ID who owns the contact
        contact_uid: The unique ID of the contact to update
        first_name: New first name (optional)
        last_name: New last name (optional)
        nickname: New nickname (optional)
        phone_number: New phone number (optional)
        email: New email address (optional)
        
    Returns:
        Success message with updated details or error message
    """
    updates = {}
    
    if first_name:
        updates["FirstName"] = first_name
    if last_name:
        updates["LastName"] = last_name
    if nickname:
        updates["nickname"] = nickname
    if phone_number:
        updates["phoneNumber"] = phone_number
    if email:
        updates["email"] = email
    
    if not updates:
        return "No updates provided. Please specify at least one field to update."
    
    result = update_contact(user_id, contact_uid, updates)
    
    if "error" in result:
        return f"Failed to update contact: {result['error']}"
    
    return f"Contact updated successfully: {result.get('message', 'Contact updated')}"

@tool
def get_contacts_tool(user_id: str) -> str:
    """
    Get all contacts for a user with completion status.
    
    Args:
        user_id: The user ID to get contacts for
        
    Returns:
        Formatted list of contacts with their information and completion status
    """
    result = get_user_contacts(user_id)
    
    if "error" in result:
        return f"Failed to get contacts: {result['error']}"
    
    contacts = result.get("contacts", [])
    total = result.get("total_contacts", 0)
    complete = result.get("complete_contacts", 0)
    partial = result.get("partial_contacts", 0)
    
    if not contacts:
        return f"No contacts found for user {user_id}"
    
    output = f"Contacts for user {user_id} ({total} total, {complete} complete, {partial} partial):\n\n"
    
    for contact in contacts:
        uid = contact.get("uid", "")
        name_parts = []
        if contact.get("FirstName"):
            name_parts.append(contact["FirstName"])
        if contact.get("LastName"):
            name_parts.append(contact["LastName"])
        
        name = " ".join(name_parts) if name_parts else "No name"
        nickname = f" ({contact['nickname']})" if contact.get("nickname") else ""
        email = contact.get("email", "")
        phone = contact.get("phoneNumber", "No phone")
        missing = contact.get("missing_fields", [])
        
        output += f"• {name}{nickname}\n"
        output += f"  Email: {email}\n"
        output += f"  Phone: {phone}\n"
        output += f"  UID: {uid}\n"
        if missing:
            output += f"  Missing: {', '.join(missing)}\n"
        output += "\n"
    
    return output

@tool
def add_memory_tool(user_id: str, memory_text: str, contact_email: Optional[str] = None) -> str:
    """
    Add a memory to the vector database for a user or contact.
    
    Args:
        user_id: The user ID to store the memory for
        memory_text: The memory content to store
        contact_email: Optional contact email to associate the memory with
        
    Returns:
        Success message or error message
    """
    result = add_memory(user_id, memory_text, contact_email)
    
    if "error" in result:
        return f"Failed to add memory: {result['error']}"
    
    return f"Memory added successfully: {result.get('message', 'Memory stored')}"

@tool
def search_memory_tool(user_id: str, query: str, max_results: int = 5) -> str:
    """
    Search memories using natural language queries.
    
    Args:
        user_id: The user ID to search memories for
        query: Natural language search query
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Formatted search results or error message
    """
    result = search_memory(user_id, query, max_results)
    
    if "error" in result:
        return f"Failed to search memory: {result['error']}"
    
    memories = result.get("memories", [])
    total = result.get("total_results", 0)
    
    if not memories:
        return f"No memories found for query: '{query}'"
    
    output = f"Memory search results for '{query}' ({total} found):\n\n"
    
    for i, memory in enumerate(memories, 1):
        memory_text = memory.get("memory", "")
        collection = memory.get("collection", "")
        score = memory.get("similarity_score", 0)
        
        output += f"{i}. {memory_text}\n"
        output += f"   Collection: {collection}, Similarity: {score:.3f}\n\n"
    
    return output

@tool
def write_status_tool(agent_id: str, agent_type: str, conversation_id: str, update: str) -> str:
    """
    Write a status update for an agent in a conversation.
    
    Args:
        agent_id: Unique identifier for the agent
        agent_type: Type of agent (e.g., 'assistant', 'whatsapp_agent')
        conversation_id: ID of the conversation
        update: Status update message
        
    Returns:
        Success message or error message
    """
    result = write_status_update(agent_id, agent_type, conversation_id, update)
    
    if "error" in result:
        return f"Failed to write status: {result['error']}"
    
    return f"Status update written successfully: {result.get('message', 'Status recorded')}"

@tool
def read_status_tool(conversation_id: str, agent_type: Optional[str] = None, agent_id: Optional[str] = None) -> str:
    """
    Read status updates for a conversation with optional filtering.
    
    Args:
        conversation_id: ID of the conversation
        agent_type: Optional agent type filter
        agent_id: Optional specific agent ID filter
        
    Returns:
        Formatted status updates or error message
    """
    result = read_status_updates(conversation_id, agent_type, agent_id)
    
    if "error" in result:
        return f"Failed to read status: {result['error']}"
    
    updates = result.get("status_updates", [])
    total = result.get("total_results", 0)
    
    if not updates:
        return f"No status updates found for conversation {conversation_id}"
    
    output = f"Status updates for conversation {conversation_id} ({total} total):\n\n"
    
    for update in updates:
        agent_id = update.get("agent_id", "")
        agent_type = update.get("agent_type", "")
        timestamp = update.get("timestamp", "")
        message = update.get("update", "")
        
        output += f"[{timestamp}] {agent_type}/{agent_id}:\n"
        output += f"  {message}\n\n"
    
    return output

@tool
def store_documents_tool(collection_name: str, documents: List[str], document_ids: Optional[List[str]] = None, metadata: Optional[str] = None) -> str:
    """
    Store documents in the vector database for semantic search.
    
    Args:
        collection_name: Name of the collection to store documents in
        documents: List of document texts to store
        document_ids: Optional list of document IDs (auto-generated if not provided)
        metadata: Optional JSON string of metadata for documents
        
    Returns:
        Success message or error message
    """
    metadatas = None
    if metadata:
        try:
            metadatas = json.loads(metadata)
            if not isinstance(metadatas, list):
                metadatas = [metadatas] * len(documents)
        except json.JSONDecodeError:
            return "Invalid metadata JSON format"
    
    result = add_vector_documents(collection_name, documents, document_ids, metadatas)
    
    if "error" in result:
        return f"Failed to store documents: {result['error']}"
    
    return f"Documents stored successfully: {result.get('message', 'Documents added')}"

@tool
def search_documents_tool(collection_name: str, query: str, max_results: int = 5, metadata_filter: Optional[str] = None) -> str:
    """
    Search documents in the vector database using semantic similarity.
    
    Args:
        collection_name: Name of the collection to search
        query: Search query text
        max_results: Maximum number of results to return (default: 5)
        metadata_filter: Optional JSON string for metadata filtering
        
    Returns:
        Formatted search results or error message
    """
    where = None
    if metadata_filter:
        try:
            where = json.loads(metadata_filter)
        except json.JSONDecodeError:
            return "Invalid metadata filter JSON format"
    
    result = query_vector_documents(collection_name, [query], max_results, where, ["documents", "metadatas", "distances"])
    
    if "error" in result:
        return f"Failed to search documents: {result['error']}"
    
    results = result.get("results", {})
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    if not documents:
        return f"No documents found for query: '{query}'"
    
    output = f"Document search results for '{query}' in collection '{collection_name}':\n\n"
    
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        output += f"{i}. {doc}\n"
        if meta:
            output += f"   Metadata: {meta}\n"
        output += f"   Similarity: {1-dist:.3f}\n\n"
    
    return output

def get_global_tools():
    """Return list of all global tools for the WhatsApp agent"""
    return [
        web_search,
        add_contact_tool,
        update_contact_tool,
        get_contacts_tool,
        add_memory_tool,
        search_memory_tool,
        write_status_tool,
        read_status_tool,
        store_documents_tool,
        search_documents_tool
    ]
