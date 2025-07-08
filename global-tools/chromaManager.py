"""
ChromaDB Manager for vector database operations
"""

import requests
import numpy as np
import base64
import sys
from typing import List, Union, Dict, Any, Optional
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from fastapi import HTTPException
import logging
import traceback
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def test_chroma_connection():
    """Test the connection to ChromaDB and verify environment variables."""
    required_vars = ["CHROMA_HOST", "CHROMA_PORT", "CHROMA_SERVER_AUTHN_CREDENTIALS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logging.error("Please set them in your .env file or environment")
        sys.exit(1)
        
    try:
        # Encode credentials for Basic Auth
        credentials = os.getenv("CHROMA_SERVER_AUTHN_CREDENTIALS")
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Initialize client with basic auth
        client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST"),
            port=int(os.getenv("CHROMA_PORT")),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            ),
            headers={
                "Authorization": f"Basic {encoded_credentials}"
            }
        )
        
        # Get tenant and database info
        try:
            # Check if we can access the default tenant
            client.tenant = "default_tenant"
            client.database = "default_database"
            
            # Test connection with heartbeat
            client.heartbeat()
            logging.info("Successfully connected to ChromaDB")
            return client
            
        except Exception as e:
            logging.error(f"Error accessing tenant/database: {str(e)}")
            raise
        
    except Exception as e:
        logging.error(f"Failed to connect to ChromaDB: {str(e)}")
        sys.exit(1)

class RemoteEmbeddingFunction:
    """A class that mimics ChromaDB's EmbeddingFunction interface"""
    
    def __init__(self, api_url: str = None):
        """Initialize with the API URL"""
        if api_url is None:
            api_url = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:5000")
        self.api_url = api_url.rstrip('/')
        
        # Test connection
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to embedding service at {self.api_url}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to embedding service at {self.api_url}: {str(e)}")

    def name(self) -> str:
        """Return the name of the embedding function for ChromaDB to use."""
        return self.api_url
        
    def __call__(self, input: Union[str, List[str]]) -> np.ndarray:
        """
        Call the embedding function on the input.
        Args:
            input: A string or list of strings to embed (ChromaDB's expected parameter name)
        Returns:
            A numpy array of embeddings
        """
        # Handle single text case
        if isinstance(input, str):
            input = [input]
            
        # Call the API
        response = requests.post(
            f"{self.api_url}/embed",
            json={"texts": input},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.json().get('error', 'Unknown error')}")
            
        # Convert to numpy array
        embeddings = np.array(response.json()['embeddings'], dtype=np.float32)
        return embeddings


class ChromaManager:
    """Manager for ChromaDB operations with remote embedding support"""
    
    def __init__(self, host: str = None, port: int = None, 
                 auth_token: Optional[str] = None, embedding_api_url: Optional[str] = None):
        """
        Initialize ChromaDB client
        
        Args:
            host: ChromaDB server host (defaults to env CHROMA_HOST)
            port: ChromaDB server port (defaults to env CHROMA_PORT)
            auth_token: Optional authentication token (defaults to env CHROMA_SERVER_AUTHN_CREDENTIALS)
            embedding_api_url: URL for our local embedding API (defaults to env EMBEDDING_SERVICE_URL)
        """
        # Use environment variables as defaults
        self.host = host or os.getenv("CHROMA_HOST", "35.195.71.55")
        self.port = port or int(os.getenv("CHROMA_PORT", "8000"))
        self.auth_token = auth_token or os.getenv("CHROMA_SERVER_AUTHN_CREDENTIALS")
        
        # Initialize embedding function
        self.embedding_api_url = embedding_api_url or os.getenv("EMBEDDING_SERVICE_URL")
        if self.embedding_api_url:
            self.embedding_function = RemoteEmbeddingFunction(api_url=self.embedding_api_url)
            logger.info(f"Using remote embedding function at {self.embedding_api_url}")
        else:
            self.embedding_function = None
            logger.warning("No embedding API URL provided. Collections will use default on-server embedding function.")
        
        # Configure ChromaDB client
        if self.auth_token:
            # Encode credentials for Basic Auth
            encoded_credentials = base64.b64encode(self.auth_token.encode()).decode()
            
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                ),
                headers={
                    "Authorization": f"Basic {encoded_credentials}"
                }
            )
            
            # Set tenant and database
            try:
                self.client.tenant = "default_tenant"
                self.client.database = "default_database"
            except Exception as e:
                logger.warning(f"Could not set tenant/database: {str(e)}")
                
            logger.info(f"ChromaDB client initialized for {self.host}:{self.port} with authentication")
        else:
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(allow_reset=True)
            )
            logger.info(f"ChromaDB client initialized for {self.host}:{self.port} without authentication")
        
        # Test connection
        try:
            self.client.heartbeat()
            logger.info(f"ChromaDB heartbeat successful")
        except Exception as e:
            logger.error(f"ChromaDB connection test failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Check if ChromaDB server is accessible"""
        try:
            heartbeat = self.client.heartbeat()
            logger.info(f"ChromaDB heartbeat successful: {heartbeat}")
            return {
                "status": "healthy",
                "heartbeat": heartbeat,
                "host": f"{self.host}:{self.port}",
                "auth_enabled": bool(self.auth_token)
            }
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "host": f"{self.host}:{self.port}",
                "auth_enabled": bool(self.auth_token)
            }

    def list_collections(self) -> Dict[str, Any]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            logger.info(f"Found {len(collections)} collections")
            collection_names = [col.name for col in collections]
            
            return {
                "collections": collection_names,
                "collection_count": len(collection_names),
                "connection_status": "connected",
                "host": self.host,
                "port": self.port
            }
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return {
                "collections": [],
                "collection_count": 0,
                "connection_status": "error",
                "host": self.host,
                "port": self.port
            }

    def get_or_create_collection(self, collection_name: str, metadata: Optional[Dict] = None) -> Any:
        """
        Get or create a collection with the configured embedding function.
        
        Args:
            collection_name: Name of the collection
            metadata: Optional metadata for the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            logger.info(f"Getting or creating collection '{collection_name}'")
            
            # Ensure metadata is not empty (required by updated ChromaDB server)
            if not metadata:
                metadata = {"created_by": "prosus-global-tools", "type": "user_collection"}
            
            # Create collection with our configured embedding function
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata=metadata,
                embedding_function=self.embedding_function
            )
            
            logger.info(f"Successfully got/created collection '{collection_name}'")
            return collection
            
        except Exception as e:
            error_msg = f"ChromaDB collection creation error for '{collection_name}': {e}"
            logger.error(error_msg)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Host: {self.host}:{self.port}, Auth: {'Yes' if self.auth_token else 'No'}")
            logger.error("Traceback:")
            logger.error(traceback.format_exc())
            raise Exception(error_msg)

    def add_documents(self, collection_name: str, documents: List[str], 
                     metadatas: Optional[List[Dict]] = None, 
                     ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add documents to a collection. Embeddings are handled by the collection's embedding function.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
            
        Returns:
            Result information
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add documents. ChromaDB will use the collection's embedding function.
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return {
                "collection": collection_name,
                "added_count": len(documents),
                "document_ids": ids
            }
            
        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {e}")
            raise

    def query_documents(self, collection_name: str, query_texts: List[str], 
                       n_results: int = 10, where: Optional[Dict] = None,
                       include: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Query documents in a collection. Embeddings are handled by the collection's embedding function.
        
        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return
            where: Optional metadata filter
            include: Optional list of fields to include in results
            
        Returns:
            Query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Prepare query parameters
            query_params = {
                "query_texts": query_texts,
                "n_results": n_results
            }
            
            if where:
                query_params["where"] = where
                
            if include:
                query_params["include"] = include
            
            # Query the collection. ChromaDB will use the collection's embedding function.
            results = collection.query(**query_params)
            
            logger.info(f"Query completed for collection '{collection_name}', found {len(results['ids'][0]) if results['ids'] else 0} results")
            return {
                "collection": collection_name,
                "results": results,
                "query_count": len(query_texts)
            }
            
        except Exception as e:
            logger.error(f"Failed to query collection '{collection_name}': {e}")
            raise

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            
            # Check if embedding function is available
            embedding_function_available = self.embedding_function is not None
            if embedding_function_available:
                try:
                    self.embedding_function(["test"])
                except Exception:
                    embedding_function_available = False
            
            return {
                "name": collection_name,
                "document_count": count,
                "metadata": collection.metadata or {},
                "embedding_function_available": embedding_function_available
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for '{collection_name}': {e}")
            raise

    def update_documents(self, collection_name: str, ids: List[str], 
                        documents: Optional[List[str]] = None,
                        metadatas: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Update documents in a collection. Embeddings are handled by the collection's embedding function.
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to update
            documents: Optional new document texts
            metadatas: Optional new metadata
            
        Returns:
            Update result
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            update_params = {"ids": ids}
            
            if documents:
                update_params["documents"] = documents
                
            if metadatas:
                update_params["metadatas"] = metadatas
            
            collection.update(**update_params)
            
            logger.info(f"Updated {len(ids)} documents in collection '{collection_name}'")
            return {
                "collection": collection_name,
                "updated_count": len(ids),
                "updated_ids": ids
            }
            
        except Exception as e:
            logger.error(f"Failed to update documents in '{collection_name}': {e}")
            raise

    def delete_documents(self, collection_name: str, ids: List[str]) -> Dict[str, Any]:
        """Delete documents from a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} documents from collection '{collection_name}'")
            return {
                "collection": collection_name,
                "deleted_count": len(ids),
                "deleted_ids": ids
            }
            
        except Exception as e:
            logger.error(f"Failed to delete documents from '{collection_name}': {e}")
            raise

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection '{collection_name}'")
            return {
                "collection": collection_name,
                "status": "deleted"
            }
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise

    def is_connected(self) -> bool:
        """Check if ChromaDB connection is available"""
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB connection check failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get ChromaDB connection status and statistics"""
        try:
            if not self.is_connected():
                return {
                    "status": "disconnected",
                    "message": "ChromaDB connection not available",
                    "host": f"{self.host}:{self.port}",
                    "embedding_service": self.embedding_api_url,
                    "authentication_enabled": bool(self.auth_token)
                }
            
            try:
                collections = self.client.list_collections()
                collection_names = [col.name for col in collections]
            except Exception as e:
                logger.warning(f"Could not list collections: {e}")
                collections = []
                collection_names = []
            
            return {
                "status": "connected",
                "message": "ChromaDB is operational",
                "host": f"{self.host}:{self.port}",
                "embedding_service": self.embedding_api_url,
                "authentication_enabled": bool(self.auth_token),
                "collection_count": len(collection_names),
                "collections": collection_names
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting ChromaDB status: {str(e)}",
                "host": f"{self.host}:{self.port}",
                "authentication_enabled": bool(self.auth_token)
            }


# Test connection function that can be called independently
def test_and_create_chroma_manager():
    """Test ChromaDB connection and create manager if successful"""
    try:
        # Test connection first
        test_client = test_chroma_connection()
        logging.info("ChromaDB connection test successful, creating manager...")
        
        # If test passes, create the manager
        return ChromaManager()
    except Exception as e:
        logging.error(f"ChromaDB connection test failed: {str(e)}")
        return None

# Global instance - create with error handling
try:
    chroma_manager = ChromaManager()
except Exception as e:
    logger.error(f"Failed to initialize global ChromaManager: {e}")
    chroma_manager = None 