"""
Configuration settings for Agno-AGI Marketing Automation System.

This module provides type-safe configuration management using Pydantic settings.
All environment variables are validated and provide sensible defaults.
"""

from typing import Optional, Literal
from pydantic import BaseSettings, Field, validator
from pathlib import Path
import os


class LLMSettings(BaseSettings):
    """Language model configuration settings."""
    
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    default_provider: Literal["openai", "anthropic"] = Field("openai", env="DEFAULT_MODEL_PROVIDER")
    default_model_id: str = Field("gpt-4o-mini", env="DEFAULT_MODEL_ID")
    max_context_length: int = Field(8000, env="MAX_CONTEXT_LENGTH")
    default_temperature: float = Field(0.7, env="DEFAULT_TEMPERATURE")
    
    @validator("openai_api_key", "anthropic_api_key")
    def validate_api_keys(cls, v):
        if v and not v.startswith(("sk-", "claude-")):
            raise ValueError("Invalid API key format")
        return v


class MarketingAPISettings(BaseSettings):
    """Marketing and sales API configuration."""
    
    apollo_api_key: Optional[str] = Field(None, env="APOLLO_API_KEY")
    builtwith_api_key: Optional[str] = Field(None, env="BUILTWITH_API_KEY")
    hubspot_api_key: Optional[str] = Field(None, env="HUBSPOT_API_KEY")
    
    # Salesforce configuration
    salesforce_username: Optional[str] = Field(None, env="SALESFORCE_USERNAME")
    salesforce_password: Optional[str] = Field(None, env="SALESFORCE_PASSWORD")
    salesforce_security_token: Optional[str] = Field(None, env="SALESFORCE_SECURITY_TOKEN")
    
    # Rate limiting
    apollo_rate_limit: int = Field(100, env="APOLLO_RATE_LIMIT")
    hubspot_rate_limit: int = Field(100, env="HUBSPOT_RATE_LIMIT")
    salesforce_rate_limit: int = Field(100, env="SALESFORCE_RATE_LIMIT")


class SocialMediaSettings(BaseSettings):
    """Social media and news API configuration."""
    
    newsapi_key: Optional[str] = Field(None, env="NEWSAPI_KEY")
    twitter_bearer_token: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    twitter_api_key: Optional[str] = Field(None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(None, env="TWITTER_API_SECRET")
    
    linkedin_username: Optional[str] = Field(None, env="LINKEDIN_USERNAME")
    linkedin_password: Optional[str] = Field(None, env="LINKEDIN_PASSWORD")


class SearchSettings(BaseSettings):
    """Search and knowledge API configuration."""
    
    tavily_api_key: Optional[str] = Field(None, env="TAVILY_API_KEY")
    serp_api_key: Optional[str] = Field(None, env="SERP_API_KEY")


class DatabaseSettings(BaseSettings):
    """Database and storage configuration."""
    
    database_url: str = Field("sqlite:///./agno_marketing.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Vector database
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(None, env="PINECONE_ENVIRONMENT")
    chroma_db_path: str = Field("./data/chroma_db", env="CHROMA_DB_PATH")


class MemorySettings(BaseSettings):
    """Memory and knowledge management configuration."""
    
    memory_provider: Literal["redis", "sqlite", "memory"] = Field("redis", env="MEMORY_PROVIDER")
    vector_store_provider: Literal["chroma", "pinecone", "faiss"] = Field("chroma", env="VECTOR_STORE_PROVIDER")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")


class SecuritySettings(BaseSettings):
    """Security and authentication configuration."""
    
    jwt_secret_key: str = Field("your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    encryption_key: Optional[str] = Field(None, env="ENCRYPTION_KEY")
    
    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration."""
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    prometheus_port: int = Field(9090, env="PROMETHEUS_PORT")


class AppSettings(BaseSettings):
    """Main application settings."""
    
    debug: bool = Field(False, env="DEBUG")
    environment: Literal["development", "staging", "production"] = Field("development", env="ENVIRONMENT")
    
    # Sub-settings
    llm: LLMSettings = LLMSettings()
    marketing_apis: MarketingAPISettings = MarketingAPISettings()
    social_media: SocialMediaSettings = SocialMediaSettings()
    search: SearchSettings = SearchSettings()
    database: DatabaseSettings = DatabaseSettings()
    memory: MemorySettings = MemorySettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get the application settings instance."""
    return settings


def validate_required_apis() -> dict[str, bool]:
    """Validate that required API keys are configured."""
    validations = {
        "llm_provider": bool(settings.llm.openai_api_key or settings.llm.anthropic_api_key),
        "apollo": bool(settings.marketing_apis.apollo_api_key),
        "hubspot": bool(settings.marketing_apis.hubspot_api_key),
        "salesforce": bool(
            settings.marketing_apis.salesforce_username and 
            settings.marketing_apis.salesforce_password
        ),
        "news": bool(settings.social_media.newsapi_key),
        "search": bool(settings.search.tavily_api_key or settings.search.serp_api_key),
    }
    return validations


def get_missing_apis() -> list[str]:
    """Get list of missing required API configurations."""
    validations = validate_required_apis()
    return [api for api, valid in validations.items() if not valid]