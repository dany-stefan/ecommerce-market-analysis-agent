"""
Logging configuration for the agent.
Simple setup using loguru for clean, readable logs.
"""

import sys
from loguru import logger
from config.settings import settings


def setup_logging():
    """
    Configure logging based on settings.
    
    Design Decision: Use loguru for simplicity - no complex configuration needed.
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with appropriate level
    log_level = "DEBUG" if settings.verbose_logging else "INFO"
    
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Optionally add file handler
    logger.add(
        "logs/agent.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )
    
    return logger
