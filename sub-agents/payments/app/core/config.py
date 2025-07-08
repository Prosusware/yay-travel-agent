"""
Configuration settings for the Checkout Agent API
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # =============================================================================
    # API Configuration
    # =============================================================================
    app_name: str = "Checkout Agent API"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("ENV", "development") == "development"
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8080"))  # Use PORT env var
    log_level: str = "INFO"
    
    # =============================================================================
    # API Keys for External Services
    # =============================================================================
    # LMNR Project API Key 
    lmnr_project_api_key: Optional[str] = None
    
    # Google API Key (for Gemini model - currently used in booking_agent.py)
    google_api_key: Optional[str] = None
    
    # Anthropic API Key (if switching to Claude model)
    anthropic_api_key: Optional[str] = None
    
    # OpenAI API Key (if needed for other integrations)
    openai_api_key: Optional[str] = None

    # Skyvern API Key (for skyvern browser automation)
    skyvern_api_key: Optional[str] = None
    
    # Webhook Configuration
    webhook_base_url: str = "http://localhost:8080"
    
    # =============================================================================
    # Security and CORS
    # =============================================================================
    # Secret key for JWT tokens (if implementing auth)
    secret_key: str = "your_secret_key_here_change_in_production"
    
    # CORS origins (comma-separated)
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins to list."""
        origins = self.cors_origins.split(",")
        return [origin.strip() for origin in origins if origin.strip()]
    
    def validate_api_keys(self) -> None:
        """Validate that required API keys are present."""
        if not self.lmnr_project_api_key:
            raise ValueError("LMNR_PROJECT_API_KEY is required")
        
        if not self.skyvern_api_key:
            raise ValueError("SKYVERN_API_KEY is required")
        
        if (not self.google_api_key and not self.anthropic_api_key
                and not self.openai_api_key):
            msg = (
                "Either GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY "
                "is required"
            )
            raise ValueError(msg)


# Create global settings instance
settings = Settings()

# Only validate API keys in development or when explicitly requested
if os.getenv("VALIDATE_API_KEYS", "false").lower() == "true":
    try:
        settings.validate_api_keys()
    except ValueError as e:
        print(f"API Key validation warning: {e}")
