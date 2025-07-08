"""
Status service for handling status update operations with MongoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from models import (
    WriteStatusUpdateRequest, ReadStatusUpdatesRequest,
    WriteStatusUpdateResponse, ReadStatusUpdatesResponse, StatusUpdateResponse
)
from validation import validate_user_id

class StatusService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def write_status_update(self, request: WriteStatusUpdateRequest) -> WriteStatusUpdateResponse:
        """Write a status update to the Status_updates collection"""
        # Validate database connection
        if not self.db_manager.is_connected():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Database Unavailable",
                    "message": "Database connection not available",
                    "details": "Cannot write status update - MongoDB connection is down",
                    "endpoint": "/api/status/write"
                }
            )
        
        # Validate required fields
        self._validate_status_update_fields(request)
        
        # Generate unique status update ID and timestamp
        status_update_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create status update document
        status_update_document = {
            "_id": status_update_id,
            "agent_id": request.agent_id.strip(),
            "agent_type": request.agent_type.strip(),
            "conversation_id": request.conversation_id.strip(),
            "update": request.update.strip(),
            "timestamp": timestamp
        }
        
        # Insert into MongoDB
        try:
            result = self.db_manager.client["Prosusware"]["Status_updates"].insert_one(status_update_document)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Insert Failed",
                        "message": "Status update was not inserted into database",
                        "details": "Database insert operation did not return an ID",
                        "endpoint": "/api/status/write"
                    }
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Insert Error",
                    "message": "Failed to insert status update into database",
                    "details": str(e),
                    "endpoint": "/api/status/write"
                }
            )
        
        return WriteStatusUpdateResponse(
            message="Status update successfully written",
            status_update_id=status_update_id,
            agent_id=request.agent_id.strip(),
            agent_type=request.agent_type.strip(),
            conversation_id=request.conversation_id.strip(),
            timestamp=timestamp.isoformat()
        )

    def read_status_updates(self, request: ReadStatusUpdatesRequest) -> ReadStatusUpdatesResponse:
        """Read status updates from the Status_updates collection with optional filtering"""
        # Validate database connection
        if not self.db_manager.is_connected():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Database Unavailable",
                    "message": "Database connection not available",
                    "details": "Cannot read status updates - MongoDB connection is down",
                    "endpoint": "/api/status/read"
                }
            )
        
        # Validate required fields
        if not request.conversation_id or not request.conversation_id.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Conversation ID",
                    "message": "conversation_id is required and cannot be empty",
                    "details": "Please provide a valid conversation_id",
                    "endpoint": "/api/status/read"
                }
            )
        
        # Build query filter
        query_filter = {"conversation_id": request.conversation_id.strip()}
        
        # Add optional filters
        if request.agent_type and request.agent_type.strip():
            query_filter["agent_type"] = request.agent_type.strip()
            
        if request.agent_id and request.agent_id.strip():
            query_filter["agent_id"] = request.agent_id.strip()
        
        # Query status updates from MongoDB
        try:
            status_updates_cursor = self.db_manager.client["Prosusware"]["Status_updates"].find(
                query_filter
            ).sort("timestamp", 1)  # Sort by timestamp ascending (oldest first)
            
            status_updates_list = list(status_updates_cursor)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to query status updates from database",
                    "details": str(e),
                    "endpoint": "/api/status/read"
                }
            )
        
        # Convert MongoDB documents to response objects
        status_updates = []
        for doc in status_updates_list:
            status_update = StatusUpdateResponse(
                id=str(doc["_id"]),
                agent_id=doc["agent_id"],
                agent_type=doc["agent_type"],
                conversation_id=doc["conversation_id"],
                update=doc["update"],
                timestamp=doc["timestamp"]
            )
            status_updates.append(status_update)
        
        return ReadStatusUpdatesResponse(
            conversation_id=request.conversation_id.strip(),
            agent_type=request.agent_type.strip() if request.agent_type else None,
            agent_id=request.agent_id.strip() if request.agent_id else None,
            status_updates=status_updates,
            total_results=len(status_updates),
            timestamp=datetime.utcnow().isoformat()
        )

    def _validate_status_update_fields(self, request: WriteStatusUpdateRequest):
        """Validate status update request fields"""
        errors = []
        
        # Validate agent_id
        if not request.agent_id or not request.agent_id.strip():
            errors.append("agent_id is required and cannot be empty")
        elif len(request.agent_id.strip()) < 1:
            errors.append("agent_id must be at least 1 character long")
        elif len(request.agent_id.strip()) > 100:
            errors.append("agent_id cannot exceed 100 characters")
        
        # Validate agent_type
        if not request.agent_type or not request.agent_type.strip():
            errors.append("agent_type is required and cannot be empty")
        elif len(request.agent_type.strip()) < 1:
            errors.append("agent_type must be at least 1 character long")
        elif len(request.agent_type.strip()) > 50:
            errors.append("agent_type cannot exceed 50 characters")
        
        # Validate conversation_id
        if not request.conversation_id or not request.conversation_id.strip():
            errors.append("conversation_id is required and cannot be empty")
        elif len(request.conversation_id.strip()) < 1:
            errors.append("conversation_id must be at least 1 character long")
        elif len(request.conversation_id.strip()) > 100:
            errors.append("conversation_id cannot exceed 100 characters")
        
        # Validate update text
        if not request.update or not request.update.strip():
            errors.append("update is required and cannot be empty")
        elif len(request.update.strip()) < 1:
            errors.append("update must be at least 1 character long")
        elif len(request.update.strip()) > 5000:
            errors.append("update cannot exceed 5000 characters")
        
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Status update request contains invalid fields",
                    "details": errors,
                    "endpoint": "/api/status/write"
                }
            ) 