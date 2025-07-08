"""
Pydantic models for the Global Tools API
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class Contact(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    nickname: Optional[str] = None
    email: EmailStr
    phoneNumber: Optional[str] = None

class ContactUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None

class ContactResponse(BaseModel):
    uid: str
    FirstName: Optional[str]
    LastName: Optional[str]
    nickname: Optional[str]
    email: str
    phoneNumber: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

class AddContactRequest(BaseModel):
    UserID: str
    contact: Contact

class UpdateContactRequest(BaseModel):
    UserID: str
    contact_uid: str
    contact: ContactUpdate

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    services: dict

class ServiceInfoResponse(BaseModel):
    service: str
    version: str
    environment: str
    port: str
    available_tools: list
    database_status: str
    timestamp: str

class DatabaseStatsResponse(BaseModel):
    status: str
    message: str
    statistics: Optional[dict] = None
    timestamp: str

class SearchResponse(BaseModel):
    query: str
    context: str
    source_count: int
    timestamp: str

# ChromaDB related models
class AddDocumentsRequest(BaseModel):
    collection_name: str
    documents: List[str]
    ids: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None

class QueryDocumentsRequest(BaseModel):
    collection_name: str
    query_texts: List[str]
    n_results: int = 10
    where: Optional[Dict[str, Any]] = None
    include: Optional[List[str]] = None

class UpdateDocumentsRequest(BaseModel):
    collection_name: str
    ids: List[str]
    documents: Optional[List[str]] = None
    metadatas: Optional[List[Dict[str, Any]]] = None

class DeleteDocumentsRequest(BaseModel):
    collection_name: str
    ids: List[str]

class ChromaDBStatusResponse(BaseModel):
    status: str
    message: str
    host: str
    port: int
    embedding_service: Optional[str] = None
    embedding_function_available: Optional[bool] = None
    collection_count: Optional[int] = None
    collections: Optional[List[str]] = None
    timestamp: str

class CollectionInfoResponse(BaseModel):
    name: str
    document_count: int
    metadata: Dict[str, Any]
    embedding_function_available: bool

class CollectionListResponse(BaseModel):
    collections: List[str]
    collection_count: int
    connection_status: str
    host: str
    port: int

# Memory management models
class AddMemoryRequest(BaseModel):
    user_id: str
    memory: str
    contact_id: Optional[str] = None
    email: Optional[EmailStr] = None

class SearchMemoryRequest(BaseModel):
    user_id: str
    query: str
    n_results: int = 10
    search_all_collections: bool = False

class MemoryResponse(BaseModel):
    id: str
    memory: str
    memory_type: str  # "user" or "contact"
    collection_name: str
    metadata: Dict[str, Any]
    created_at: datetime
    distance: Optional[float] = None

class AddMemoryResponse(BaseModel):
    message: str
    memory_id: str
    memory_type: str
    collection_name: str
    user_id: str
    contact_id: Optional[str] = None
    timestamp: str

class SearchMemoryResponse(BaseModel):
    query: str
    user_id: str
    memories: List[MemoryResponse]
    total_results: int
    collections_searched: List[str]
    search_all_collections: bool
    timestamp: str

# Status update models
class WriteStatusUpdateRequest(BaseModel):
    agent_id: str
    agent_type: str
    conversation_id: str
    update: str

class StatusUpdateResponse(BaseModel):
    id: str
    agent_id: str
    agent_type: str
    conversation_id: str
    update: str
    timestamp: datetime

class WriteStatusUpdateResponse(BaseModel):
    message: str
    status_update_id: str
    agent_id: str
    agent_type: str
    conversation_id: str
    timestamp: str

class ReadStatusUpdatesRequest(BaseModel):
    conversation_id: str
    agent_type: Optional[str] = None
    agent_id: Optional[str] = None

class ReadStatusUpdatesResponse(BaseModel):
    conversation_id: str
    agent_type: Optional[str]
    agent_id: Optional[str]
    status_updates: List[StatusUpdateResponse]
    total_results: int
    timestamp: str 
    
class UserResponse(BaseModel):
    _id: str
    FirstName: str
    LastName: str
    email: str
    phoneNumber: Optional[str] = None
    uid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    Contacts: List[Any] = []
    Usage: Dict[str, Any] = {}

# Conversation management models
class UpdateConversationNameRequest(BaseModel):
    conversation_id: str
    name: str

class UpdateConversationNameResponse(BaseModel):
    message: str
    conversation_id: str
    name: str
    timestamp: str