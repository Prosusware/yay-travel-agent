"""
Memory service for handling memory storage and retrieval using ChromaDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from bson import ObjectId

from models import (
    AddMemoryRequest, SearchMemoryRequest, AddMemoryResponse, 
    SearchMemoryResponse, MemoryResponse
)
from validation import validate_user_id

class MemoryService:
    def __init__(self, db_manager, chroma_manager):
        self.db_manager = db_manager
        self.chroma_manager = chroma_manager

    def add_memory(self, request: AddMemoryRequest) -> AddMemoryResponse:
        """Add a memory to ChromaDB for a user or contact"""
        # Validate user ID
        user_id = validate_user_id(request.user_id, "user_id")
        
        # Validate memory content
        if not request.memory or not request.memory.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Memory",
                    "message": "Memory content cannot be empty",
                    "details": "Please provide valid memory content",
                    "endpoint": "/api/memory/add"
                }
            )
        
        memory_content = request.memory.strip()
        
        # Validate that user exists in database
        user = self._get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "User Not Found",
                    "message": f"User with ID '{user_id}' does not exist",
                    "details": "Please verify the user ID is correct",
                    "user_id": user_id,
                    "endpoint": "/api/memory/add"
                }
            )
        
        # Determine collection name and memory type
        collection_name, memory_type, contact_id = self._determine_collection_info(
            user_id, request.contact_id, request.email
        )
        
        # Generate unique memory ID
        memory_id = str(uuid.uuid4())
        
        # Create memory metadata
        metadata = self._build_memory_metadata(
            user_id, memory_type, contact_id, memory_content
        )
        
        # Add memory to ChromaDB
        try:
            self.chroma_manager.add_documents(
                collection_name=collection_name,
                documents=[memory_content],
                ids=[memory_id],
                metadatas=[metadata]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Memory Storage Error",
                    "message": "Failed to store memory in vector database",
                    "details": str(e),
                    "endpoint": "/api/memory/add"
                }
            )
        
        return AddMemoryResponse(
            message=f"Memory successfully stored as {memory_type} memory",
            memory_id=memory_id,
            memory_type=memory_type,
            collection_name=collection_name,
            user_id=user_id,
            contact_id=contact_id,
            timestamp=datetime.utcnow().isoformat()
        )

    def search_memories(self, request: SearchMemoryRequest) -> SearchMemoryResponse:
        """Search memories for a user across specified collections"""
        # Validate user ID
        user_id = validate_user_id(request.user_id, "user_id")
        
        # Validate search query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Query",
                    "message": "Search query cannot be empty",
                    "details": "Please provide a valid search query",
                    "endpoint": "/api/memory/search"
                }
            )
        
        if request.n_results <= 0 or request.n_results > 50:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Results Count",
                    "message": "n_results must be between 1 and 50",
                    "details": f"Provided n_results: {request.n_results}",
                    "endpoint": "/api/memory/search"
                }
            )
        
        search_query = request.query.strip()
        
        # Validate that user exists
        user = self._get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "User Not Found",
                    "message": f"User with ID '{user_id}' does not exist",
                    "details": "Please verify the user ID is correct",
                    "user_id": user_id,
                    "endpoint": "/api/memory/search"
                }
            )
        
        # Determine collections to search based on search_all_collections parameter
        if request.search_all_collections:
            # Search across user collection + ALL contact collections for this specific user
            # (Does NOT search other users' collections or unrelated collections)
            collections_to_search = self._get_user_collections(user_id, user)
        else:
            # Search only user's own personal collection
            collections_to_search = [user_id]
        
        if not collections_to_search:
            return SearchMemoryResponse(
                query=search_query,
                user_id=user_id,
                memories=[],
                total_results=0,
                collections_searched=[],
                search_all_collections=request.search_all_collections,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Search across specified collections
        all_memories = []
        successfully_searched = []
        
        for collection_name in collections_to_search:
            try:
                # Check if collection exists
                collection_info = self.chroma_manager.get_collection_info(collection_name)
                if collection_info["document_count"] == 0:
                    continue
                
                # Search this collection
                results = self.chroma_manager.query_documents(
                    collection_name=collection_name,
                    query_texts=[search_query],
                    n_results=request.n_results,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Process results from this collection
                collection_memories = self._process_search_results(
                    results, collection_name
                )
                all_memories.extend(collection_memories)
                successfully_searched.append(collection_name)
                
            except Exception as e:
                # Log error but continue searching other collections
                print(f"Error searching collection {collection_name}: {str(e)}")
                continue
        
        # Sort all memories by distance (most similar first)
        all_memories.sort(key=lambda x: x.distance if x.distance is not None else float('inf'))
        
        # Return top N results
        top_memories = all_memories[:request.n_results]
        
        return SearchMemoryResponse(
            query=search_query,
            user_id=user_id,
            memories=top_memories,
            total_results=len(top_memories),
            collections_searched=successfully_searched,
            search_all_collections=request.search_all_collections,
            timestamp=datetime.utcnow().isoformat()
        )

    def _determine_collection_info(self, user_id: str, contact_id: Optional[str], 
                                 email: Optional[str]) -> tuple:
        """Determine collection name, memory type, and contact ID"""
        # If both contact_id and email provided, validate they match
        if contact_id and email:
            # Validate that both refer to the same contact
            validated_contact_id = self._validate_contact_id_email_match(user_id, contact_id, email)
            return validated_contact_id, "contact", validated_contact_id
        
        # If only email provided, look up contact_id
        elif email:
            contact_id = self._get_contact_id_by_email(user_id, email)
            return contact_id, "contact", contact_id
        
        # If only contact_id provided, validate it exists
        elif contact_id:
            self._validate_contact_exists(user_id, contact_id)
            return contact_id, "contact", contact_id
        
        # No contact specified - user memory
        else:
            return user_id, "user", None

    def _validate_contact_id_email_match(self, user_id: str, contact_id: str, email: str) -> str:
        """Validate that contact_id and email refer to the same contact"""
        try:
            contact = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts": {
                    "$elemMatch": {
                        "uid": contact_id,
                        "email": email
                    }
                }
            }, {"Contacts.$": 1})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to validate contact ID and email match",
                    "details": str(e),
                    "endpoint": "/api/memory/add"
                }
            )
        
        if not contact or not contact.get("Contacts"):
            # Check if contact_id exists but with different email
            contact_by_id = self._get_contact_by_id(user_id, contact_id)
            contact_by_email = self._get_contact_by_email(user_id, email)
            
            if contact_by_id and contact_by_email:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Contact ID Email Mismatch",
                        "message": f"Contact ID '{contact_id}' and email '{email}' refer to different contacts",
                        "details": "Please ensure both contact_id and email refer to the same contact",
                        "contact_id": contact_id,
                        "email": email,
                        "user_id": user_id
                    }
                )
            elif contact_by_id:
                actual_email = contact_by_id.get("email", "unknown")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Email Mismatch",
                        "message": f"Contact ID '{contact_id}' exists but has email '{actual_email}', not '{email}'",
                        "details": "Please verify the email address is correct",
                        "contact_id": contact_id,
                        "provided_email": email,
                        "actual_email": actual_email
                    }
                )
            elif contact_by_email:
                actual_contact_id = contact_by_email.get("uid", "unknown")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Contact ID Mismatch",
                        "message": f"Email '{email}' exists but has contact ID '{actual_contact_id}', not '{contact_id}'",
                        "details": "Please verify the contact ID is correct",
                        "email": email,
                        "provided_contact_id": contact_id,
                        "actual_contact_id": actual_contact_id
                    }
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Contact Not Found",
                        "message": f"No contact found with ID '{contact_id}' and email '{email}' for user '{user_id}'",
                        "details": "Please verify both the contact ID and email are correct",
                        "contact_id": contact_id,
                        "email": email,
                        "user_id": user_id
                    }
                )
        
        return contact_id

    def _get_contact_by_id(self, user_id: str, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by contact ID"""
        try:
            user = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.uid": contact_id
            }, {"Contacts.$": 1})
            
            if user and user.get("Contacts"):
                return user["Contacts"][0]
            return None
        except Exception:
            return None

    def _get_contact_by_email(self, user_id: str, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email"""
        try:
            user = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.email": email
            }, {"Contacts.$": 1})
            
            if user and user.get("Contacts"):
                return user["Contacts"][0]
            return None
        except Exception:
            return None

    def _get_contact_id_by_email(self, user_id: str, email: str) -> str:
        """Look up contact ID by email address"""
        try:
            user = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.email": email
            }, {"Contacts.$": 1})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to look up contact by email",
                    "details": str(e),
                    "endpoint": "/api/memory/add"
                }
            )
        
        if not user or not user.get("Contacts"):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Contact Not Found",
                    "message": f"No contact found with email '{email}' for user '{user_id}'",
                    "details": "Please verify the email address is correct",
                    "email": email,
                    "user_id": user_id
                }
            )
        
        return user["Contacts"][0]["uid"]

    def _validate_contact_exists(self, user_id: str, contact_id: str):
        """Validate that contact exists for the user"""
        try:
            contact = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.uid": contact_id
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to validate contact",
                    "details": str(e),
                    "endpoint": "/api/memory/add"
                }
            )
        
        if not contact:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Contact Not Found",
                    "message": f"Contact with ID '{contact_id}' not found for user '{user_id}'",
                    "details": "Please verify the contact ID is correct",
                    "contact_id": contact_id,
                    "user_id": user_id
                }
            )

    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by their ID"""
        try:
            # Validate that the user_id is a valid ObjectId
            if not ObjectId.is_valid(user_id):
                return None # Return None if the ID is not valid, will be handled as "User Not Found"

            # Check if user exists in the database using _id
            return self.db_manager.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to query user database",
                    "details": str(e)
                }
            )

    def _build_memory_metadata(self, user_id: str, memory_type: str, 
                              contact_id: Optional[str], memory_content: str) -> Dict[str, Any]:
        """Build metadata for memory storage"""
        metadata = {
            "user_id": user_id,
            "memory_type": memory_type,
            "created_at": datetime.utcnow().isoformat(),
            "content_length": len(memory_content)
        }
        
        if contact_id:
            metadata["contact_id"] = contact_id
        
        return metadata

    def _get_user_collections(self, user_id: str, user: Dict[str, Any]) -> List[str]:
        """
        Get collection names for a specific user ONLY:
        1. User's own personal collection (user_id)
        2. All contact collections belonging to this user (contact.uid for each contact)
        
        This method NEVER returns collections from other users or unrelated collections.
        """
        collections = []
        
        # Add user's own personal collection
        collections.append(user_id)
        
        # Add contact collections that belong to this specific user
        contacts = user.get("Contacts", [])
        for contact in contacts:
            contact_id = contact.get("uid")
            if contact_id:
                collections.append(contact_id)
        
        return collections

    def _process_search_results(self, results: Dict[str, Any], 
                               collection_name: str) -> List[MemoryResponse]:
        """Process ChromaDB search results into MemoryResponse objects"""
        memories = []
        
        # Extract results
        query_results = results.get("results", {})
        ids = query_results.get("ids", [[]])[0] if query_results.get("ids") else []
        documents = query_results.get("documents", [[]])[0] if query_results.get("documents") else []
        metadatas = query_results.get("metadatas", [[]])[0] if query_results.get("metadatas") else []
        distances = query_results.get("distances", [[]])[0] if query_results.get("distances") else []
        
        for i in range(len(ids)):
            memory_id = ids[i]
            memory_content = documents[i]
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else None
            
            # Parse created_at
            created_at_str = metadata.get("created_at", datetime.utcnow().isoformat())
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except:
                created_at = datetime.utcnow()
            
            memory = MemoryResponse(
                id=memory_id,
                memory=memory_content,
                memory_type=metadata.get("memory_type", "unknown"),
                collection_name=collection_name,
                metadata=metadata,
                created_at=created_at,
                distance=distance
            )
            memories.append(memory)
        
        return memories 