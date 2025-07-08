"""
Contact service for handling contact-related business logic
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any
from fastapi import HTTPException

from models import Contact, ContactUpdate, ContactResponse, AddContactRequest, UpdateContactRequest
from validation import (
    validate_database_connection, validate_user_id, 
    validate_contact_fields, validate_update_fields, raise_validation_error
)

class ContactService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_contact(self, request: AddContactRequest) -> Dict[str, Any]:
        """Add a new contact to a user's contact list"""
        # Validate database connection
        validate_database_connection(self.db_manager, "/api/contacts/add")
        
        # Validate UserID
        user_id = validate_user_id(request.UserID)
        
        # Validate contact fields
        errors = validate_contact_fields(request.contact)
        raise_validation_error(errors, "/api/contacts/add", "Contact information contains invalid fields")
        
        # Generate unique ID for the contact
        contact_uid = str(uuid.uuid4())
        
        # Create contact document
        contact_document = self._build_contact_document(request.contact, contact_uid)
        
        # Check if user exists
        user = self._get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "User Not Found",
                    "message": f"User with ID '{user_id}' does not exist",
                    "details": "Please verify the UserID is correct",
                    "user_id": user_id
                }
            )
        
        # Check for duplicate email
        self._check_duplicate_email(user_id, request.contact.email)
        
        # Add contact to user's Contacts array
        self._insert_contact_to_user(user_id, contact_document)
        
        # Determine if contact is partial
        is_partial = any(v is None for v in [
            request.contact.FirstName, request.contact.LastName, request.contact.phoneNumber
        ])
        
        message = ("Contact added successfully with partial information" 
                  if is_partial else "Contact added successfully")
        
        return {
            "message": message,
            "contact": ContactResponse(**contact_document),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "You can update this contact later with additional information using the update endpoint"
        }

    def update_contact(self, request: UpdateContactRequest) -> Dict[str, Any]:
        """Update an existing contact with additional information"""
        # Validate database connection
        validate_database_connection(self.db_manager, "/api/contacts/update")
        
        # Validate UserID and contact_uid
        user_id = validate_user_id(request.UserID)
        contact_uid = validate_user_id(request.contact_uid, "contact_uid")
        
        # Validate update fields
        errors = validate_update_fields(request.contact)
        raise_validation_error(errors, "/api/contacts/update", "Contact update information contains invalid fields")
        
        # Check if user exists and has the specified contact
        user = self._get_user_with_contact(user_id, contact_uid)
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "User or Contact Not Found",
                    "message": f"User '{user_id}' or contact '{contact_uid}' does not exist",
                    "details": "Please verify both the UserID and contact UID are correct",
                    "user_id": user_id,
                    "contact_uid": contact_uid
                }
            )
        
        # If email is being updated, check for duplicates
        if request.contact.email:
            self._check_duplicate_email_for_update(user_id, contact_uid, request.contact.email)
        
        # Build and execute update
        update_doc = self._build_update_document(request.contact)
        fields_updated = self._update_contact_in_db(user_id, contact_uid, update_doc)
        
        # Retrieve updated contact
        updated_contact = self._get_updated_contact(user_id, contact_uid)
        
        return {
            "message": "Contact updated successfully",
            "contact": ContactResponse(**updated_contact),
            "user_id": user_id,
            "fields_updated": fields_updated,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_user_contacts(self, user_id: str) -> Dict[str, Any]:
        """Get all contacts for a specific user with completion status"""
        # Validate database connection
        validate_database_connection(self.db_manager, "/api/contacts/{user_id}")
        
        # Validate user_id
        user_id = validate_user_id(user_id, "User ID")
        
        # Query user and contacts
        user = self._get_user_contacts_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "User Not Found",
                    "message": f"User with ID '{user_id}' does not exist",
                    "details": "Please verify the user ID is correct",
                    "user_id": user_id,
                    "endpoint": "/api/contacts/{user_id}"
                }
            )
        
        contacts = user.get("Contacts", [])
        
        # Categorize contacts as complete or partial
        complete_contacts, partial_contacts = self._categorize_contacts(contacts)
        
        return {
            "user_id": user_id,
            "contacts": contacts,
            "total_contacts": len(contacts),
            "complete_contacts": len(complete_contacts),
            "partial_contacts": len(partial_contacts),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _build_contact_document(self, contact: Contact, contact_uid: str) -> Dict[str, Any]:
        """Build contact document for database insertion"""
        return {
            "uid": contact_uid,
            "FirstName": contact.FirstName.strip() if contact.FirstName else None,
            "LastName": contact.LastName.strip() if contact.LastName else None,
            "nickname": contact.nickname.strip() if contact.nickname else None,
            "email": contact.email,
            "phoneNumber": contact.phoneNumber.strip() if contact.phoneNumber else None,
            "created_at": datetime.utcnow()
        }

    def _build_update_document(self, contact: ContactUpdate) -> Dict[str, Any]:
        """Build update document for contact modification"""
        update_doc = {"$set": {}}
        
        if contact.FirstName is not None:
            update_doc["$set"]["Contacts.$.FirstName"] = contact.FirstName.strip()
        if contact.LastName is not None:
            update_doc["$set"]["Contacts.$.LastName"] = contact.LastName.strip()
        if contact.nickname is not None:
            update_doc["$set"]["Contacts.$.nickname"] = contact.nickname.strip()
        if contact.email is not None:
            update_doc["$set"]["Contacts.$.email"] = contact.email
        if contact.phoneNumber is not None:
            update_doc["$set"]["Contacts.$.phoneNumber"] = contact.phoneNumber.strip()
        
        # Always update the contact's updated_at timestamp
        update_doc["$set"]["Contacts.$.updated_at"] = datetime.utcnow()
        update_doc["$set"]["updated_at"] = datetime.utcnow()
        
        return update_doc

    def _get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        try:
            return self.db_manager.users.find_one({"uid": user_id})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to query user database",
                    "details": f"Error checking if user exists: {str(e)}",
                    "endpoint": "/api/contacts/add"
                }
            )

    def _get_user_with_contact(self, user_id: str, contact_uid: str) -> Dict[str, Any]:
        """Get user with specific contact"""
        try:
            return self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.uid": contact_uid
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to query user and contact",
                    "details": f"Error checking if user and contact exist: {str(e)}",
                    "endpoint": "/api/contacts/update"
                }
            )

    def _get_user_contacts_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user contacts by ID"""
        try:
            return self.db_manager.users.find_one(
                {"uid": user_id},
                {"Contacts": 1, "_id": 0}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to query user contacts",
                    "details": f"Error retrieving user data: {str(e)}",
                    "user_id": user_id,
                    "endpoint": "/api/contacts/{user_id}"
                }
            )

    def _check_duplicate_email(self, user_id: str, email: str):
        """Check for duplicate email in user's contacts"""
        try:
            existing_contact = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts.email": email
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to check for duplicate contacts",
                    "details": f"Error checking duplicate email: {str(e)}",
                    "endpoint": "/api/contacts/add"
                }
            )
        
        if existing_contact:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Duplicate Contact",
                    "message": f"Contact with email '{email}' already exists for this user",
                    "details": "Each user can only have one contact per email address. Use the update endpoint to modify existing contacts.",
                    "email": email,
                    "user_id": user_id
                }
            )

    def _check_duplicate_email_for_update(self, user_id: str, contact_uid: str, email: str):
        """Check for duplicate email when updating contact"""
        try:
            existing_email = self.db_manager.users.find_one({
                "uid": user_id,
                "Contacts": {
                    "$elemMatch": {
                        "email": email,
                        "uid": {"$ne": contact_uid}
                    }
                }
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to check for duplicate email",
                    "details": f"Error checking duplicate email: {str(e)}",
                    "endpoint": "/api/contacts/update"
                }
            )
        
        if existing_email:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Duplicate Email",
                    "message": f"Another contact with email '{email}' already exists for this user",
                    "details": "Each user can only have one contact per email address",
                    "email": email,
                    "user_id": user_id
                }
            )

    def _insert_contact_to_user(self, user_id: str, contact_document: Dict[str, Any]):
        """Insert contact into user's contacts array"""
        try:
            result = self.db_manager.users.update_one(
                {"uid": user_id},
                {
                    "$push": {"Contacts": contact_document},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Update Error",
                    "message": "Failed to add contact to user",
                    "details": f"Error updating user document: {str(e)}",
                    "endpoint": "/api/contacts/add"
                }
            )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Update Failed",
                    "message": "Contact was not added to user",
                    "details": "Database update operation did not modify any documents",
                    "user_id": user_id
                }
            )

    def _update_contact_in_db(self, user_id: str, contact_uid: str, update_doc: Dict[str, Any]) -> List[str]:
        """Update contact in database and return list of updated fields"""
        try:
            result = self.db_manager.users.update_one(
                {
                    "uid": user_id,
                    "Contacts.uid": contact_uid
                },
                update_doc
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Update Error",
                    "message": "Failed to update contact",
                    "details": f"Error updating contact document: {str(e)}",
                    "endpoint": "/api/contacts/update"
                }
            )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Update Failed",
                    "message": "Contact was not updated",
                    "details": "Database update operation did not modify any documents",
                    "user_id": user_id,
                    "contact_uid": contact_uid
                }
            )
        
        return list(update_doc["$set"].keys())

    def _get_updated_contact(self, user_id: str, contact_uid: str) -> Dict[str, Any]:
        """Retrieve updated contact from database"""
        try:
            updated_user = self.db_manager.users.find_one(
                {"uid": user_id},
                {"Contacts": {"$elemMatch": {"uid": contact_uid}}, "_id": 0}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "Failed to retrieve updated contact",
                    "details": f"Error retrieving updated contact: {str(e)}",
                    "endpoint": "/api/contacts/update"
                }
            )
        
        if not updated_user or not updated_user.get("Contacts"):
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Contact Retrieval Failed",
                    "message": "Could not retrieve updated contact information",
                    "details": "Contact was updated but could not be retrieved",
                    "user_id": user_id,
                    "contact_uid": contact_uid
                }
            )
        
        return updated_user["Contacts"][0]

    def _categorize_contacts(self, contacts: List[Dict[str, Any]]) -> tuple:
        """Categorize contacts as complete or partial"""
        complete_contacts = []
        partial_contacts = []
        
        for contact in contacts:
            required_fields = ["FirstName", "LastName", "phoneNumber"]
            missing_fields = [field for field in required_fields if not contact.get(field)]
            
            if missing_fields:
                contact["missing_fields"] = missing_fields
                partial_contacts.append(contact)
            else:
                complete_contacts.append(contact)
        
        return complete_contacts, partial_contacts 