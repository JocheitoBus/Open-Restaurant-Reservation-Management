"""
Configuration module for the Reservation System.

Uses Pydantic Settings v2 for environment variable management and validation.
"""

from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name: Application name
        app_version: Application version
        debug: Debug mode flag
        database_url: SQLite database connection URL
        sql_echo: Whether to echo SQL statements
        environment: Current environment (development, staging, production)
        api_v1_prefix: API v1 prefix for routes
        restaurant_hours_start: Restaurant opening hour (24-hour format)
        restaurant_hours_end: Restaurant closing hour (24-hour format)
    """
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
    
    app_name: str = "Restaurant Reservation System"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///reservation_system.db"
    sql_echo: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    restaurant_hours_start: int = 10  # 10:00 AM
    restaurant_hours_end: int = 22  # 10:00 PM
    
    # API Key for authentication (development only)
    api_key: str = "dev-api-key-change-in-production"


settings = Settings()
