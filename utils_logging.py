import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Set up a logger with console and optional file output.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_app_logger(log_file: str = "app.log") -> logging.Logger:
    """Get the main application logger."""
    return setup_logger("chirp-api", "INFO", log_file)


def log_request(logger: logging.Logger, method: str, endpoint: str, status_code: int = None):
    """Log HTTP request information."""
    if status_code:
        logger.info(f"{method} {endpoint} - {status_code}")
    else:
        logger.info(f"{method} {endpoint}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log error with context information."""
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True)