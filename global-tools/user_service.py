"""
User service for handling user-related business logic
"""
from fastapi import HTTPException
from bson import ObjectId

class UserService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_user_by_id(self, user_id: str):
        """Get a single user by their MongoDB _id"""
        try:
            # Validate that the user_id is a valid ObjectId
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid User ID",
                        "message": f"The provided user_id '{user_id}' is not a valid MongoDB ObjectId.",
                        "user_id": user_id
                    }
                )
            
            user = self.db_manager.users.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "User Not Found",
                        "message": f"User with _id '{user_id}' not found.",
                        "user_id": user_id
                    }
                )
            
            # Convert ObjectId to string for JSON serialization
            user["_id"] = str(user["_id"])
            return user

        except HTTPException as e:
            # Re-raise HTTPException to be handled by FastAPI
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Database Query Error",
                    "message": "An unexpected error occurred while fetching the user.",
                    "details": str(e)
                }
            ) 