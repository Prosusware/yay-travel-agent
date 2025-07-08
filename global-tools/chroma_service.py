"""
ChromaDB service for handling vector database operations
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from datetime import datetime

from models import (
    AddDocumentsRequest, QueryDocumentsRequest, UpdateDocumentsRequest,
    DeleteDocumentsRequest, CollectionInfoResponse, CollectionListResponse
)
from validation import validate_user_id

class ChromaService:
    def __init__(self, chroma_manager):
        self.chroma_manager = chroma_manager

    def add_documents(self, request: AddDocumentsRequest) -> Dict[str, Any]:
        """Add documents to a ChromaDB collection"""
        # Validate inputs
        if not request.documents:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Documents",
                    "message": "Documents list cannot be empty",
                    "details": "At least one document must be provided",
                    "endpoint": "/api/vector/documents/add"
                }
            )
        
        if len(request.documents) != len(request.ids):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Mismatched Arrays",
                    "message": "Documents and IDs arrays must have the same length",
                    "details": f"Documents: {len(request.documents)}, IDs: {len(request.ids)}",
                    "endpoint": "/api/vector/documents/add"
                }
            )
        
        if request.metadatas and len(request.metadatas) != len(request.documents):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Mismatched Metadata",
                    "message": "Metadatas array must have the same length as documents",
                    "details": f"Documents: {len(request.documents)}, Metadatas: {len(request.metadatas)}",
                    "endpoint": "/api/vector/documents/add"
                }
            )
        
        # Validate collection name
        collection_name = self._validate_collection_name(request.collection_name)
        
        # Add documents using ChromaManager
        result = self.chroma_manager.add_documents(
            collection_name=collection_name,
            documents=request.documents,
            ids=request.ids,
            metadatas=request.metadatas
        )
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    def query_documents(self, request: QueryDocumentsRequest) -> Dict[str, Any]:
        """Query documents from a ChromaDB collection"""
        # Validate inputs
        if not request.query_texts:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Query",
                    "message": "Query texts list cannot be empty",
                    "details": "At least one query text must be provided",
                    "endpoint": "/api/vector/documents/query"
                }
            )
        
        if request.n_results <= 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Results Count",
                    "message": "n_results must be greater than 0",
                    "details": f"Provided n_results: {request.n_results}",
                    "endpoint": "/api/vector/documents/query"
                }
            )
        
        # Validate collection name
        collection_name = self._validate_collection_name(request.collection_name)
        
        # Query documents using ChromaManager
        result = self.chroma_manager.query_documents(
            collection_name=collection_name,
            query_texts=request.query_texts,
            n_results=request.n_results,
            where=request.where,
            include=request.include
        )
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    def update_documents(self, request: UpdateDocumentsRequest) -> Dict[str, Any]:
        """Update documents in a ChromaDB collection"""
        # Validate inputs
        if not request.ids:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid IDs",
                    "message": "IDs list cannot be empty",
                    "details": "At least one document ID must be provided",
                    "endpoint": "/api/vector/documents/update"
                }
            )
        
        if not request.documents and not request.metadatas:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No Update Data",
                    "message": "Either documents or metadatas must be provided for update",
                    "details": "At least one field (documents or metadatas) must be specified",
                    "endpoint": "/api/vector/documents/update"
                }
            )
        
        if request.documents and len(request.documents) != len(request.ids):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Mismatched Arrays",
                    "message": "Documents and IDs arrays must have the same length",
                    "details": f"Documents: {len(request.documents)}, IDs: {len(request.ids)}",
                    "endpoint": "/api/vector/documents/update"
                }
            )
        
        if request.metadatas and len(request.metadatas) != len(request.ids):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Mismatched Metadata",
                    "message": "Metadatas and IDs arrays must have the same length",
                    "details": f"Metadatas: {len(request.metadatas)}, IDs: {len(request.ids)}",
                    "endpoint": "/api/vector/documents/update"
                }
            )
        
        # Validate collection name
        collection_name = self._validate_collection_name(request.collection_name)
        
        # Update documents using ChromaManager
        result = self.chroma_manager.update_documents(
            collection_name=collection_name,
            ids=request.ids,
            documents=request.documents,
            metadatas=request.metadatas
        )
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    def delete_documents(self, request: DeleteDocumentsRequest) -> Dict[str, Any]:
        """Delete documents from a ChromaDB collection"""
        # Validate inputs
        if not request.ids:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid IDs",
                    "message": "IDs list cannot be empty",
                    "details": "At least one document ID must be provided",
                    "endpoint": "/api/vector/documents/delete"
                }
            )
        
        # Validate collection name
        collection_name = self._validate_collection_name(request.collection_name)
        
        # Delete documents using ChromaManager
        result = self.chroma_manager.delete_documents(
            collection_name=collection_name,
            ids=request.ids
        )
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    def get_collection_info(self, collection_name: str) -> CollectionInfoResponse:
        """Get information about a specific collection"""
        # Validate collection name
        collection_name = self._validate_collection_name(collection_name)
        
        # Get collection info using ChromaManager
        info = self.chroma_manager.get_collection_info(collection_name)
        
        return CollectionInfoResponse(**info)

    def list_collections(self) -> CollectionListResponse:
        """List all collections"""
        # List collections using ChromaManager
        result = self.chroma_manager.list_collections()
        
        return CollectionListResponse(**result)

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection"""
        # Validate collection name
        collection_name = self._validate_collection_name(collection_name)
        
        # Delete collection using ChromaManager
        result = self.chroma_manager.delete_collection(collection_name)
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    def _validate_collection_name(self, collection_name: str) -> str:
        """Validate collection name"""
        if not collection_name or not collection_name.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid Collection Name",
                    "message": "Collection name cannot be empty or null",
                    "details": "Please provide a valid collection name",
                    "field": "collection_name"
                }
            )
        
        collection_name = collection_name.strip()
        
        if len(collection_name) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Collection Name Too Short",
                    "message": "Collection name must be at least 2 characters long",
                    "details": f"Provided name '{collection_name}' is only {len(collection_name)} character(s)",
                    "collection_name": collection_name
                }
            )
        
        if len(collection_name) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Collection Name Too Long",
                    "message": "Collection name cannot exceed 100 characters",
                    "details": f"Provided name is {len(collection_name)} characters long",
                    "max_length": 100
                }
            )
        
        return collection_name 