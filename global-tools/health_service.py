"""
Health service for system status and health checks
"""

import os
from datetime import datetime
from typing import Dict, Any

from models import HealthResponse, ServiceInfoResponse, DatabaseStatsResponse, ChromaDBStatusResponse

class HealthService:
    def __init__(self, db_manager, search_service, chroma_manager=None):
        self.db_manager = db_manager
        self.search_service = search_service
        self.chroma_manager = chroma_manager

    def get_health_status(self) -> HealthResponse:
        """Get comprehensive health status of all services"""
        services = {
            "database": "up" if self.db_manager.is_connected() else "down",
            "search": "up" if self.search_service.is_available() else "down"
        }
        
        # Add ChromaDB status if manager is available
        if self.chroma_manager:
            services["vector_database"] = "up" if self.chroma_manager.is_connected() else "down"
        
        all_services_up = all(status == "up" for status in services.values())
        overall_status = "healthy" if all_services_up else "degraded"
        
        message = ("All services operational" if all_services_up 
                  else "Some services are unavailable")
        
        return HealthResponse(
            status=overall_status,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            services=services
        )

    def get_service_info(self) -> ServiceInfoResponse:
        """Get detailed service information"""
        db_status = "connected" if self.db_manager.is_connected() else "disconnected"
        
        available_tools = ["web_search", "contact_management", "memory_management", "health_monitoring"]
        if self.chroma_manager:
            available_tools.append("vector_database")
        
        return ServiceInfoResponse(
            service="Global Tools API",
            version="1.0.0",
            environment=os.getenv("ENV", "development"),
            port=os.getenv("PORT", "8000"),
            available_tools=available_tools,
            database_status=db_status,
            timestamp=datetime.utcnow().isoformat()
        )

    def get_database_stats(self) -> DatabaseStatsResponse:
        """Get database status and statistics"""
        if not self.db_manager.is_connected():
            return DatabaseStatsResponse(
                status="disconnected",
                message="Database connection not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            stats = self.db_manager.get_database_stats()
            return DatabaseStatsResponse(
                status="connected",
                message="Database is operational",
                statistics=stats,
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return DatabaseStatsResponse(
                status="error",
                message=f"Failed to retrieve database statistics: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )

    def get_chroma_status(self) -> ChromaDBStatusResponse:
        """Get ChromaDB status and statistics"""
        if not self.chroma_manager:
            return ChromaDBStatusResponse(
                status="unavailable",
                message="ChromaDB manager not initialized",
                host="unknown",
                port=0,
                timestamp=datetime.utcnow().isoformat()
            )
        
        status_data = self.chroma_manager.get_status()
        
        return ChromaDBStatusResponse(
            status=status_data["status"],
            message=status_data["message"],
            host=status_data["host"],
            port=status_data.get("port", 0),
            embedding_service=status_data.get("embedding_service"),
            embedding_function_available=status_data.get("embedding_function_available"),
            collection_count=status_data.get("collection_count"),
            collections=status_data.get("collections"),
            timestamp=datetime.utcnow().isoformat()
        ) 