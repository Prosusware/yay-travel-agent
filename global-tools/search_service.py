"""
Search service for handling search operations using Tavily API
"""

import os
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException

import tavily
from validation import validate_search_query
from models import SearchResponse

class SearchService:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = tavily.TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search(self, query: str) -> SearchResponse:
        """Perform search using Tavily API"""
        # Validate query
        validated_query = validate_search_query(query)
        
        # Check if Tavily is available
        if not self.client:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Search Service Unavailable",
                    "message": "Search functionality is not available",
                    "details": "TAVILY_API_KEY environment variable is not configured",
                    "endpoint": "/api/search"
                }
            )
        
        try:
            # Use context search for LLM optimization
            response = self.client.get_search_context(
                query=validated_query,
                search_depth="advanced",
                max_tokens=8000
            )
            
            # Extract context from response
            context = response if isinstance(response, str) else str(response)
            
            # Estimate source count (approximation based on context length)
            estimated_sources = max(1, len(context) // 500)
            
            return SearchResponse(
                query=validated_query,
                context=context,
                source_count=estimated_sources,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Search Request Failed",
                    "message": "Failed to execute search query",
                    "details": f"Tavily API error: {str(e)}",
                    "query": validated_query,
                    "endpoint": "/api/search"
                }
            )

    def is_available(self) -> bool:
        """Check if search service is available"""
        return self.client is not None 