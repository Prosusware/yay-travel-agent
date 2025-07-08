"""
Conversation service for handling conversation-related business logic
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException

from models import UpdateConversationNameRequest, UpdateConversationNameResponse
from validation import validate_database_connection

class ConversationService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def update_conversation_name(self, request: UpdateConversationNameRequest) -> UpdateConversationNameResponse:
        """Update the name field of a conversation in the Conversations collection"""
        # Validate database connection
        validate_database_connection(self.db_manager, "/api/conversations/name")
        
        # Validate conversation_id
        conversation_id = self._validate_conversation_id(request.conversation_id)
        
        # Validate name
        name = self._validate_name(request.name)
        
        # Get the Conversations collection
        conversations_collection = self._get_conversations_collection()
        
        # Update the conversation name
        result = self._update_conversation_name_in_db(conversations_collection, conversation_id, name)
        
        return UpdateConversationNameResponse(
            message="Conversation name updated successfully",
            conversation_id=conversation_id,
            name=name,
            timestamp=datetime.utcnow().isoformat()
        )

    def _validate_conversation_id(self, conversation_id: str) -> str:
        """Validate conversation ID"""
        if not conversation_id or not conversation_id.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Conversation ID",
                    "message": "conversation_id is required and cannot be empty",
                    "details": "Please provide a valid conversation_id",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        conversation_id = conversation_id.strip()
        
        if len(conversation_id) < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Conversation ID",
                    "message": "conversation_id must be at least 1 character long",
                    "details": "Please provide a valid conversation_id",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        if len(conversation_id) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Conversation ID",
                    "message": "conversation_id cannot exceed 100 characters",
                    "details": "Please provide a shorter conversation_id",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        return conversation_id

    def _validate_name(self, name: str) -> str:
        """Validate conversation name"""
        if not name or not name.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Name",
                    "message": "name is required and cannot be empty",
                    "details": "Please provide a valid name for the conversation",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        name = name.strip()
        
        if len(name) < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Name",
                    "message": "name must be at least 1 character long",
                    "details": "Please provide a valid name",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        if len(name) > 500:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Name",
                    "message": "name cannot exceed 500 characters",
                    "details": "Please provide a shorter name",
                    "endpoint": "/api/conversations/name"
                }
            )
        
        return name

    def _get_conversations_collection(self):
        """Get the Conversations collection"""
        try:
            return self.db_manager.database["Conversations"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Connection Error",
                    "message": "Failed to access Conversations collection",
                    "details": str(e),
                    "endpoint": "/api/conversations/name"
                }
            )

    def _update_conversation_name_in_db(self, conversations_collection, conversation_id: str, name: str) -> Dict[str, Any]:
        """Update conversation name in the database"""
        try:
            # Only update existing conversations, do not create new ones
            result = conversations_collection.update_one(
                {"_id": conversation_id},
                {
                    "$set": {
                        "name": name,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Conversation Not Found",
                        "message": f"Conversation with ID '{conversation_id}' does not exist",
                        "details": "Please verify the conversation_id is correct",
                        "conversation_id": conversation_id,
                        "endpoint": "/api/conversations/name"
                    }
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Update Error",
                    "message": "Failed to update conversation name in database",
                    "details": str(e),
                    "conversation_id": conversation_id,
                    "endpoint": "/api/conversations/name"
                }
            )
