"""
Configuration settings for the e-commerce agent.
Uses Pydantic for validation and python-dotenv for environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Design Decision: Using Pydantic for settings management provides:
    - Type validation
    - Clear documentation of required configuration
    - Easy testing with override values
    """
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    max_tokens: int = 2000
    
    # Agent Configuration
    max_iterations: int = 5
    verbose_logging: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
