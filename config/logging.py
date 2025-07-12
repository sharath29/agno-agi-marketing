"""
Logging configuration for Agno-AGI Marketing Automation System.

Provides structured logging with different outputs for development and production.
"""

import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from .settings import get_settings


def setup_logging() -> None:
    """Set up application logging configuration."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Console logging for development
    if settings.debug:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.monitoring.log_level,
            colorize=True,
        )
    else:
        # Structured JSON logging for production
        logger.add(
            sys.stdout,
            format="{time} | {level} | {name}:{function}:{line} | {message}",
            level=settings.monitoring.log_level,
            serialize=True,
        )

    # File logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "agno_marketing.log",
        rotation="1 day",
        retention="30 days",
        level=settings.monitoring.log_level,
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
    )

    # Error logging
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        rotation="1 week",
        retention="12 weeks",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
    )

    # Agent-specific logging
    logger.add(
        log_dir / "agents.log",
        filter=lambda record: "agent" in record["extra"],
        level="DEBUG" if settings.debug else "INFO",
        rotation="1 day",
        retention="7 days",
        format="{time} | {level} | Agent: {extra[agent]} | {message}",
    )

    # API call logging
    logger.add(
        log_dir / "api_calls.log",
        filter=lambda record: "api" in record["extra"],
        level="INFO",
        rotation="1 day",
        retention="14 days",
        format="{time} | {level} | API: {extra[api]} | {message}",
    )


def get_agent_logger(agent_name: str):
    """Get a logger instance for a specific agent."""
    return logger.bind(agent=agent_name)


def get_api_logger(api_name: str):
    """Get a logger instance for API calls."""
    return logger.bind(api=api_name)


def log_agent_action(agent_name: str, action: str, details: Dict[str, Any] = None):
    """Log an agent action with structured data."""
    agent_logger = get_agent_logger(agent_name)
    message = f"Action: {action}"
    if details:
        message += f" | Details: {details}"
    agent_logger.info(message)


def log_api_call(api_name: str, endpoint: str, status: str, duration: float = None):
    """Log an API call with performance metrics."""
    api_logger = get_api_logger(api_name)
    message = f"Endpoint: {endpoint} | Status: {status}"
    if duration:
        message += f" | Duration: {duration:.2f}s"
    api_logger.info(message)


# Initialize logging on module import
setup_logging()
