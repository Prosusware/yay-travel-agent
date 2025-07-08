import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_CONNECTION_STRING")
DATABASE_NAME = "Whatsapp"
PROCESSED_MESSAGES_COLLECTION = "whatsapp"
MONITORING_LOGS_COLLECTION = "monitoring_logs"

# Initialize MongoDB client
mongo_client = None
db = None

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, db
    try:
        # Print the MongoDB URL (with password masked for security)
        connection_string = MONGODB_URL or os.getenv("MONGODB_CONNECTION_STRING")
        if connection_string:
            print(f"Attempting to connect to MongoDB")
        else:
            print("ERROR: No MongoDB connection string found. Please set MONGODB_CONNECTION_STRING in your environment.")
            return False
        
        mongo_client = MongoClient(connection_string)
        # Test the connection
        mongo_client.admin.command('ping')
        db = mongo_client[DATABASE_NAME]
        
        print(f"Connected to MongoDB database: {DATABASE_NAME}")
        print(f"Collections: {db.list_collection_names()}")
        
        # Create indexes for better performance
        db[PROCESSED_MESSAGES_COLLECTION].create_index("message_id", unique=True)
        db[MONITORING_LOGS_COLLECTION].create_index("timestamp")
        
        # Test reading a document
        test_doc = db[PROCESSED_MESSAGES_COLLECTION].find_one()
        if test_doc:
            print(f"Test document read successfully: {test_doc}")
        else:
            print("No documents found in the collection.")
        
        print("MongoDB connected successfully")
        return True
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"MongoDB initialization error: {str(e)}")
        return False

def close_mongodb():
    """Close MongoDB connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed")

def save_processed_message_to_db(msg_id: str, msg_data: Dict[str, Any] = None):
    """Save a processed message ID to MongoDB"""
    if db is None:
        print(f"Cannot save message {msg_id} to MongoDB: database connection not initialized")
        return False
    
    try:
        document = {
            "message_id": msg_id,
            "timestamp": datetime.now(),
            "message_data": msg_data or {}
        }
        
        # Print debug info about what we're saving
        print(f"Saving message to MongoDB: {msg_id}")
        if msg_data:
            content = msg_data.get('content', '')
            sender = msg_data.get('sender', '')
            chat = msg_data.get('chat_name', '')
            print(f"Message details - Sender: {sender}, Chat: {chat}, Content: {content[:50]}...")
        
        result = db[PROCESSED_MESSAGES_COLLECTION].insert_one(document)
        print(f"Message saved to MongoDB with ID: {result.inserted_id}")
        return True
    except DuplicateKeyError:
        # Message already exists, which is fine
        print(f"Message {msg_id} already exists in MongoDB (duplicate key)")
        return True
    except Exception as e:
        print(f"Error saving processed message to DB: {e}")
        return False

def is_message_processed_in_db(message_id: str) -> bool:
    """Check if a message has already been processed in MongoDB"""
    if db is None:
        return False
    
    try:
        doc = db[PROCESSED_MESSAGES_COLLECTION].find_one({"message_id": message_id})
        return doc is not None
    except Exception as e:
        print(f"Error checking message in DB: {e}")
        return False

def get_processed_messages_from_db(limit: int = 1000) -> List[str]:
    """Get list of processed message IDs from MongoDB"""
    if db is None:
        return []
    
    try:
        cursor = db[PROCESSED_MESSAGES_COLLECTION].find({}, {"message_id": 1}).sort("timestamp", -1).limit(limit)
        return [doc["message_id"] for doc in cursor]
    except Exception as e:
        print(f"Error getting processed messages from DB: {e}")
        return []

def save_monitoring_log_to_db(log_type: str, message: str, details: Dict[str, Any] = None):
    """Save a monitoring log entry to MongoDB"""
    if db is None:
        return False
    
    try:
        document = {
            "timestamp": datetime.now(),
            "type": log_type,
            "message": message,
            "details": details or {}
        }
        db[MONITORING_LOGS_COLLECTION].insert_one(document)
        return True
    except Exception as e:
        print(f"Error saving monitoring log to DB: {e}")
        return False

def get_monitoring_logs_from_db(limit: int = 50) -> List[Dict[str, Any]]:
    """Get monitoring logs from MongoDB"""
    if db is None:
        return []
    
    try:
        cursor = db[MONITORING_LOGS_COLLECTION].find({}).sort("timestamp", -1).limit(limit)
        logs = []
        for doc in cursor:
            log_entry = {
                "timestamp": doc["timestamp"].isoformat(),
                "type": doc["type"],
                "message": doc["message"],
                "details": doc.get("details", {})
            }
            logs.append(log_entry)
        return logs
    except Exception as e:
        print(f"Error getting monitoring logs from DB: {e}")
        return []

def clear_monitoring_logs_in_db():
    """Clear all monitoring logs from MongoDB"""
    if db is None:
        return False
    
    try:
        db[MONITORING_LOGS_COLLECTION].delete_many({})
        return True
    except Exception as e:
        print(f"Error clearing monitoring logs in DB: {e}")
        return False

def clear_processed_messages_in_db():
    """Clear all processed messages from MongoDB"""
    if db is None:
        return False
    
    try:
        db[PROCESSED_MESSAGES_COLLECTION].delete_many({})
        return True
    except Exception as e:
        print(f"Error clearing processed messages in DB: {e}")
        return False

def load_processed_messages_from_db(limit: int = 5000):
    """Load processed messages from MongoDB into memory on startup"""
    if db is None:
        return []
    
    try:
        # Load recent processed messages (last 5000 to keep memory usage reasonable)
        processed_ids = get_processed_messages_from_db(limit)
        print(f"Loaded {len(processed_ids)} processed message IDs from MongoDB")
        return processed_ids
    except Exception as e:
        print(f"Error loading processed messages from DB: {e}")
        return []

def load_monitoring_logs_from_db(limit: int = 1000):
    """Load monitoring logs from MongoDB into memory on startup"""
    if db is None:
        return []
    
    try:
        # Load recent logs (last 1000 to keep memory usage reasonable)
        logs = get_monitoring_logs_from_db(limit)
        print(f"Loaded {len(logs)} monitoring logs from MongoDB")
        return logs
    except Exception as e:
        print(f"Error loading monitoring logs from DB: {e}")
        return []

def get_database_stats():
    """Get database statistics"""
    if db is None:
        return {
            "status": "disconnected",
            "message": "MongoDB is not connected"
        }
    
    try:
        # Get collection stats
        processed_count = db[PROCESSED_MESSAGES_COLLECTION].count_documents({})
        logs_count = db[MONITORING_LOGS_COLLECTION].count_documents({})
        
        # Get recent activity
        recent_processed = db[PROCESSED_MESSAGES_COLLECTION].count_documents({
            "timestamp": {"$gte": datetime.now() - timedelta(hours=24)}
        })
        recent_logs = db[MONITORING_LOGS_COLLECTION].count_documents({
            "timestamp": {"$gte": datetime.now() - timedelta(hours=24)}
        })
        
        return {
            "status": "connected",
            "database": DATABASE_NAME,
            "collections": {
                "processed_messages": {
                    "total": processed_count,
                    "last_24h": recent_processed
                },
                "monitoring_logs": {
                    "total": logs_count,
                    "last_24h": recent_logs
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get database stats: {str(e)}"
        }

def get_processed_messages(limit: int = 50, skip: int = 0):
    """Get processed messages with their data from MongoDB"""
    if db is None:
        return {
            "status": "disconnected",
            "message": "MongoDB is not connected",
            "messages": []
        }
    
    try:
        cursor = db[PROCESSED_MESSAGES_COLLECTION].find({}).sort("timestamp", -1).skip(skip).limit(limit)
        messages = []
        
        for doc in cursor:
            message_entry = {
                "message_id": doc["message_id"],
                "timestamp": doc["timestamp"].isoformat(),
                "message_data": doc.get("message_data", {})
            }
            messages.append(message_entry)
        
        total_count = db[PROCESSED_MESSAGES_COLLECTION].count_documents({})
        
        return {
            "status": "connected",
            "messages": messages,
            "total": total_count,
            "returned": len(messages),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get processed messages: {str(e)}",
            "messages": []
        }

def search_processed_messages(
    sender: Optional[str] = None,
    chat_name: Optional[str] = None,
    content: Optional[str] = None,
    limit: int = 50
):
    """Search processed messages by sender, chat name, or content"""
    if db is None:
        return {
            "status": "disconnected",
            "message": "MongoDB is not connected",
            "messages": []
        }
    
    try:
        # Build search query
        query = {}
        if sender:
            query["message_data.sender"] = {"$regex": sender, "$options": "i"}
        if chat_name:
            query["message_data.chat_name"] = {"$regex": chat_name, "$options": "i"}
        if content:
            query["message_data.content"] = {"$regex": content, "$options": "i"}
        
        cursor = db[PROCESSED_MESSAGES_COLLECTION].find(query).sort("timestamp", -1).limit(limit)
        messages = []
        
        for doc in cursor:
            message_entry = {
                "message_id": doc["message_id"],
                "timestamp": doc["timestamp"].isoformat(),
                "message_data": doc.get("message_data", {})
            }
            messages.append(message_entry)
        
        return {
            "status": "connected",
            "messages": messages,
            "search_criteria": {
                "sender": sender,
                "chat_name": chat_name,
                "content": content
            },
            "results_count": len(messages)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search processed messages: {str(e)}",
            "messages": []
        }

def test_mongodb_connection():
    """Test MongoDB connection and return status"""
    global db
    
    # Check if MongoDB is initialized
    if db is None:
        connection_string = MONGODB_URL or os.getenv("MONGODB_CONNECTION_STRING")
        return {
            "status": "disconnected",
            "message": "MongoDB is not connected",
            "connection_string_exists": bool(connection_string),
            "database_name": DATABASE_NAME,
            "collections": {
                "processed_messages": PROCESSED_MESSAGES_COLLECTION,
                "monitoring_logs": MONITORING_LOGS_COLLECTION
            }
        }
    
    try:
        # Test the connection with a ping
        mongo_client.admin.command('ping')
        
        # Get database stats
        collections = db.list_collection_names()
        processed_count = db[PROCESSED_MESSAGES_COLLECTION].count_documents({})
        logs_count = db[MONITORING_LOGS_COLLECTION].count_documents({})
        
        # Try to insert a test document
        test_id = f"test_{datetime.now().isoformat()}"
        test_result = db[PROCESSED_MESSAGES_COLLECTION].insert_one({
            "message_id": test_id,
            "timestamp": datetime.now(),
            "message_data": {
                "test": True,
                "generated_at": datetime.now().isoformat()
            }
        })
        
        return {
            "status": "connected",
            "database": DATABASE_NAME,
            "collections": collections,
            "counts": {
                "processed_messages": processed_count,
                "monitoring_logs": logs_count
            },
            "test_insert": {
                "success": bool(test_result.inserted_id),
                "test_id": test_id
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB test failed: {str(e)}",
            "error_type": type(e).__name__
        }

def get_processed_message_from_db(message_id: str) -> Dict[str, Any]:
    """Get a specific processed message by ID from MongoDB"""
    if db is None:
        return None
    
    try:
        doc = db[PROCESSED_MESSAGES_COLLECTION].find_one({"message_id": message_id})
        if doc and "_id" in doc:
            # Convert ObjectId to string for JSON serialization
            doc["_id"] = str(doc["_id"])
        
        # Convert timestamp to ISO format string if it exists
        if doc and "timestamp" in doc and isinstance(doc["timestamp"], datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()
            
        return doc
    except Exception as e:
        print(f"Error retrieving message from DB: {e}")
        return None

def load_monitoring_logs_from_db() -> List[Dict[str, Any]]:
    """Load monitoring logs from MongoDB into memory on startup"""
    if db is None:
        return []
    
    try:
        # Load recent logs (last 1000 to keep memory usage reasonable)
        logs = get_monitoring_logs_from_db(1000)
        print(f"Loaded {len(logs)} monitoring logs from MongoDB")
        return logs
    except Exception as e:
        print(f"Error loading monitoring logs from DB: {e}")
        return []

def save_task_to_db(conversation_id: str, task: str, metadata: Dict[str, Any] = None):
    """Save a task for a conversation ID to MongoDB"""
    if db is None:
        print(f"Cannot save task for conversation {conversation_id} to MongoDB: database connection not initialized")
        return False
    
    try:
        document = {
            "conversation_id": conversation_id,
            "task": task,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        # Use upsert to replace existing task for the same conversation
        result = db["conversation_tasks"].replace_one(
            {"conversation_id": conversation_id}, 
            document, 
            upsert=True
        )
        print(f"Task saved for conversation {conversation_id}")
        return True
    except Exception as e:
        print(f"Error saving task to DB: {e}")
        return False

def get_task_by_conversation_id(conversation_id: str) -> Dict[str, Any]:
    """Get the stored task for a conversation ID from MongoDB"""
    if db is None:
        return None
    
    try:
        doc = db["conversation_tasks"].find_one({"conversation_id": conversation_id})
        if doc and "_id" in doc:
            # Convert ObjectId to string for JSON serialization
            doc["_id"] = str(doc["_id"])

        print("DEBUG: Retrieved task for conversation {conversation_id}: {doc}")
        
        # Convert timestamp to ISO format string if it exists
        if doc and "timestamp" in doc and isinstance(doc["timestamp"], datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()
            
        return doc
    except Exception as e:
        print(f"Error retrieving task from DB: {e}")
        return None
