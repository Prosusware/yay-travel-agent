"""
Validation utilities for the Global Tools API
"""

from fastapi import HTTPException
from typing import List, Optional
from models import Contact, ContactUpdate

def validate_database_connection(db_manager, endpoint: str):
    """Validate that database connection is available"""
    if not db_manager.is_connected():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Database Unavailable",
                "message": "Database connection not available",
                "details": "Cannot perform operation - MongoDB connection is down",
                "endpoint": endpoint
            }
        )

def validate_user_id(user_id: str, field_name: str = "UserID"):
    """Validate that user ID is not empty"""
    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid {field_name}",
                "message": f"{field_name} cannot be empty or null",
                "details": f"Please provide a valid {field_name}",
                "field": field_name
            }
        )
    return user_id.strip()

def validate_contact_fields(contact: Contact, is_update: bool = False) -> List[str]:
    """Validate contact fields and return list of errors"""
    errors = []
    
    # For new contacts, email is required
    if not is_update and not contact.email:
        errors.append("Email is required when adding a contact")
    
    # Validate non-empty fields if provided
    if contact.FirstName is not None and not contact.FirstName.strip():
        errors.append("FirstName cannot be empty string if provided")
    if contact.LastName is not None and not contact.LastName.strip():
        errors.append("LastName cannot be empty string if provided")
    if contact.nickname is not None and not contact.nickname.strip():
        errors.append("nickname cannot be empty string if provided")
    if contact.phoneNumber is not None and not contact.phoneNumber.strip():
        errors.append("phoneNumber cannot be empty string if provided")
    
    return errors

def validate_update_fields(contact: ContactUpdate) -> List[str]:
    """Validate that at least one field is provided for update"""
    errors = []
    
    update_fields = [
        contact.FirstName, contact.LastName, contact.nickname, 
        contact.email, contact.phoneNumber
    ]
    
    if all(field is None for field in update_fields):
        errors.append("At least one field must be provided for update")
    
    # Validate non-empty fields if provided
    if contact.FirstName is not None and not contact.FirstName.strip():
        errors.append("FirstName cannot be empty string if provided")
    if contact.LastName is not None and not contact.LastName.strip():
        errors.append("LastName cannot be empty string if provided")
    if contact.nickname is not None and not contact.nickname.strip():
        errors.append("nickname cannot be empty string if provided")
    if contact.phoneNumber is not None and not contact.phoneNumber.strip():
        errors.append("phoneNumber cannot be empty string if provided")
    
    return errors

def validate_search_query(query: str) -> str:
    """Validate search query parameters"""
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Query",
                "message": "Search query cannot be empty or null",
                "details": "Please provide a valid search query",
                "parameter": "query",
                "endpoint": "/api/search"
            }
        )
    
    query = query.strip()
    
    if len(query) < 2:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Query Too Short",
                "message": "Search query must be at least 2 characters long",
                "details": f"Provided query '{query}' is only {len(query)} character(s)",
                "query": query,
                "endpoint": "/api/search"
            }
        )
    
    if len(query) > 500:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Query Too Long",
                "message": "Search query cannot exceed 500 characters",
                "details": f"Provided query is {len(query)} characters long",
                "max_length": 500,
                "endpoint": "/api/search"
            }
        )
    
    return query

def raise_validation_error(errors: List[str], endpoint: str, message: str = "Invalid data provided"):
    """Raise HTTPException with validation errors"""
    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation Error",
                "message": message,
                "details": errors,
                "endpoint": endpoint
            }
        ) 