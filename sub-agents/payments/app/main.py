"""
Main FastAPI application for the Checkout Agent API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import flights, hotels, food, webhooks
from app.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="API for automated booking of flights, hotels, and food",
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(flights.router, prefix="/api/v1", tags=["flights"])
app.include_router(hotels.router, prefix="/api/v1", tags=["hotels"])
app.include_router(food.router, prefix="/api/v1", tags=["food"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"{settings.app_name} is running", 
        "status": "healthy",
        "version": settings.app_version
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )