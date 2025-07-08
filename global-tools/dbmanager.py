"""
MongoDB Database Manager for Global Tools API
Manages connections to the Prosusware database with 4 collections
"""

import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    MongoDB Database Manager for Prosusware database
    """
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.mongodb_url = os.getenv("MONGODB_URL")
        
        # Collection names for Prosusware database
        self.collection_names = {
            "users": "Users",
            "tools": "tools", 
            "sessions": "sessions",
            "analytics": "analytics"
        }
        
        # Initialize connection
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.mongodb_url:
            logger.error("MONGODB_URL environment variable not set")
            return False
        
        try:
            # Create MongoDB client with connection timeout
            self.client = MongoClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second timeout
                socketTimeoutMS=10000           # 10 second timeout
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Connect to Prosusware database
            self.database = self.client.Prosusware
            
            logger.info("Successfully connected to MongoDB - Prosusware database")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if database connection is active
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.client is None or self.database is None:
            return False
        
        try:
            # Ping the database
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Get a specific collection from the database
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Collection: MongoDB collection object or None if not connected
        """
        if not self.is_connected():
            logger.error("Database not connected")
            return None
        
        if collection_name not in self.collection_names.values():
            logger.warning(f"Collection '{collection_name}' not in predefined collections")
        
        return self.database[collection_name]
    
    @property
    def users(self) -> Optional[Collection]:
        """Get users collection"""
        return self.get_collection(self.collection_names["users"])
    
    @property
    def tools(self) -> Optional[Collection]:
        """Get tools collection"""
        return self.get_collection(self.collection_names["tools"])
    
    @property
    def sessions(self) -> Optional[Collection]:
        """Get sessions collection"""
        return self.get_collection(self.collection_names["sessions"])
    
    @property
    def analytics(self) -> Optional[Collection]:
        """Get analytics collection"""
        return self.get_collection(self.collection_names["analytics"])
    
    def create_indexes(self):
        """
        Create useful indexes for the collections
        """
        if not self.is_connected():
            logger.error("Database not connected - cannot create indexes")
            return
        
        try:
            # Users collection indexes
            if self.users is not None:
                self.users.create_index("email", unique=True)
                self.users.create_index("created_at")
                logger.info("Created indexes for users collection")
            
            # Tools collection indexes
            if self.tools is not None:
                self.tools.create_index("name")
                self.tools.create_index("category")
                self.tools.create_index("created_at")
                logger.info("Created indexes for tools collection")
            
            # Sessions collection indexes
            if self.sessions is not None:
                self.sessions.create_index("user_id")
                self.sessions.create_index("session_id", unique=True)
                self.sessions.create_index("created_at")
                self.sessions.create_index("expires_at")
                logger.info("Created indexes for sessions collection")
            
            # Analytics collection indexes
            if self.analytics is not None:
                self.analytics.create_index("event_type")
                self.analytics.create_index("user_id")
                self.analytics.create_index("timestamp")
                self.analytics.create_index([("user_id", 1), ("timestamp", -1)])
                logger.info("Created indexes for analytics collection")
                
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def get_database_stats(self) -> dict:
        """
        Get database statistics
        
        Returns:
            dict: Database statistics
        """
        if not self.is_connected():
            return {"error": "Database not connected"}
        
        try:
            stats = {
                "database_name": self.database.name,
                "collections": {}
            }
            
            for collection_key, collection_name in self.collection_names.items():
                collection = self.get_collection(collection_name)
                if collection is not None:
                    stats["collections"][collection_key] = {
                        "name": collection_name,
                        "document_count": collection.count_documents({}),
                        "indexes": len(list(collection.list_indexes()))
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    def close_connection(self):
        """
        Close the database connection
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance
    
    Returns:
        DatabaseManager: The database manager instance
    """
    return db_manager 