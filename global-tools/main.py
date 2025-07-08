"""
Global Tools API - A comprehensive FastAPI application for GCP Cloud Run
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Import models
from models import (
    AddContactRequest, UpdateContactRequest, HealthResponse, 
    ServiceInfoResponse, DatabaseStatsResponse, SearchResponse,
    ChromaDBStatusResponse, AddDocumentsRequest, QueryDocumentsRequest,
    UpdateDocumentsRequest, DeleteDocumentsRequest, CollectionInfoResponse,
    CollectionListResponse, AddMemoryRequest, SearchMemoryRequest,
    AddMemoryResponse, SearchMemoryResponse, WriteStatusUpdateRequest,
    ReadStatusUpdatesRequest, WriteStatusUpdateResponse, ReadStatusUpdatesResponse,
    UserResponse, UpdateConversationNameRequest, UpdateConversationNameResponse
)

# Import services
from dbmanager import db_manager
from contact_service import ContactService
from search_service import SearchService
from health_service import HealthService
from chromaManager import chroma_manager
from chroma_service import ChromaService
from memory_service import MemoryService
from status_service import StatusService
from user_service import UserService
from conversation_service import ConversationService

app = FastAPI(
    title="Global Tools API",
    description="A comprehensive API service providing web search, contact management, memory storage, vector database, and health monitoring tools",
    version="1.0.0"
)

# Initialize services
contact_service = ContactService(db_manager)
search_service = SearchService()
chroma_service = ChromaService(chroma_manager)
memory_service = MemoryService(db_manager, chroma_manager)
health_service = HealthService(db_manager, search_service, chroma_manager)
status_service = StatusService(db_manager)
user_service = UserService(db_manager)
conversation_service = ConversationService(db_manager)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed information"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request Validation Error",
            "message": "The request contains invalid or missing data",
            "details": errors,
            "request_method": request.method,
            "request_url": str(request.url)
        }
    )

# Routes
@app.get("/")
async def root():
    """Welcome message and API overview"""
    return {
        "message": "Welcome to Global Tools API",
        "description": "A comprehensive API service for Prosusware global operations",
        "version": "1.0.0",
        "features": [
            "Web search integration via Tavily",
            "Contact management system",
            "Memory storage and retrieval system",
            "Vector database operations with ChromaDB",
            "Database health monitoring",
            "Service status tracking",
            "Conversation management system"
        ],
        "endpoints": {
            "health": "/health",
            "info": "/api/info",
            "search": "/api/search?query=your_query",
            "contacts": "/api/contacts/add, /api/contacts/update, /api/contacts/{user_id}",
            "memory": "/api/memory/add, /api/memory/search",
            "database": "/api/database/status",
            "vector": "/api/vector/collections, /api/vector/documents/*, /api/vector/status",
            "conversations": "/api/conversations/name"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with service status monitoring"""
    return health_service.get_health_status()

@app.get("/api/info", response_model=ServiceInfoResponse)
async def get_info():
    """Get detailed service information"""
    return health_service.get_service_info()

@app.get("/api/search", response_model=SearchResponse)
async def search_web(query: str):
    """
    Search the web using Tavily API with LLM-optimized response format
    
    This endpoint provides formatted context suitable for LLM consumption,
    rather than raw search results.
    """
    return search_service.search(query)

@app.get("/api/database/status", response_model=DatabaseStatsResponse)
async def database_status():
    """Get database connection status and statistics"""
    return health_service.get_database_stats()

@app.post("/api/contacts/add")
async def add_contact(request: AddContactRequest):
    """
    Add a new contact to a user's contact list
    
    Supports partial contact information - only email is required.
    Additional fields can be added later using the update endpoint.
    """
    return contact_service.add_contact(request)

@app.patch("/api/contacts/update")
async def update_contact(request: UpdateContactRequest):
    """
    Update an existing contact with additional or modified information
    
    Allows progressive enhancement of contact data.
    At least one field must be provided for update.
    """
    return contact_service.update_contact(request)

@app.get("/api/contacts/{user_id}")
async def get_user_contacts(user_id: str):
    """
    Get all contacts for a specific user with completion status
    
    Returns contact list with indicators for complete vs partial contacts.
    """
    return contact_service.get_user_contacts(user_id)

@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get a single user by their MongoDB _id
    """
    return user_service.get_user_by_id(user_id)

@app.patch("/api/conversations/name", response_model=UpdateConversationNameResponse)
async def update_conversation_name(request: UpdateConversationNameRequest):
    """
    Update the name field of a conversation in the Conversations collection
    
    This endpoint allows the LLM to update conversation names by providing 
    a conversation_id and the new name. The conversation must already exist,
    otherwise a 404 error will be returned.
    """
    return conversation_service.update_conversation_name(request)

# Memory Management endpoints
@app.post("/api/memory/add", response_model=AddMemoryResponse)
async def add_memory(request: AddMemoryRequest):
    """
    Add a memory to the vector database for a user or contact
    
    If contact_id or email is provided, stores as a contact memory.
    If neither is provided, stores as a user memory.
    Both contact_id and email can be provided - they must refer to the same contact.
    Email addresses are looked up to find the corresponding contact ID.
    """
    return memory_service.add_memory(request)

@app.post("/api/memory/search", response_model=SearchMemoryResponse)
async def search_memory(request: SearchMemoryRequest):
    """Search memory using natural language query"""
    return memory_service.search_memories(request)

# ChromaDB / Vector Database endpoints
@app.get("/api/vector/status", response_model=ChromaDBStatusResponse)
async def vector_database_status():
    """Get ChromaDB connection status and statistics"""
    return health_service.get_chroma_status()

@app.get("/api/vector/collections", response_model=CollectionListResponse)
async def list_vector_collections():
    """List all ChromaDB collections"""
    return chroma_service.list_collections()

@app.get("/api/vector/collections/{collection_name}", response_model=CollectionInfoResponse)
async def get_collection_info(collection_name: str):
    """Get information about a specific ChromaDB collection"""
    return chroma_service.get_collection_info(collection_name)

@app.delete("/api/vector/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a ChromaDB collection"""
    return chroma_service.delete_collection(collection_name)

@app.post("/api/vector/documents/add")
async def add_documents_to_collection(request: AddDocumentsRequest):
    """
    Add documents to a ChromaDB collection
    
    Automatically creates the collection if it doesn't exist.
    Documents will be embedded using the configured embedding service.
    """
    return chroma_service.add_documents(request)

@app.post("/api/vector/documents/query")
async def query_documents_in_collection(request: QueryDocumentsRequest):
    """
    Query documents from a ChromaDB collection using semantic search
    
    Returns the most similar documents based on the query text embeddings.
    """
    return chroma_service.query_documents(request)

@app.patch("/api/vector/documents/update")
async def update_documents_in_collection(request: UpdateDocumentsRequest):
    """
    Update documents in a ChromaDB collection
    
    Can update document content and/or metadata for existing documents.
    """
    return chroma_service.update_documents(request)

@app.post("/api/vector/documents/delete")
async def delete_documents_from_collection(request: DeleteDocumentsRequest):
    """
    Delete documents from a ChromaDB collection
    
    Removes documents by their IDs from the specified collection.
    Note: Uses POST instead of DELETE to properly support request body.
    """
    return chroma_service.delete_documents(request)

# Status update endpoints
@app.post("/api/status/write", response_model=WriteStatusUpdateResponse)
async def write_status_update(request: WriteStatusUpdateRequest):
    """Write a status update to the database"""
    return status_service.write_status_update(request)

@app.post("/api/status/read", response_model=ReadStatusUpdatesResponse)
async def read_status_updates(request: ReadStatusUpdatesRequest):
    """Read status updates from the database with optional filtering"""
    return status_service.read_status_updates(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 