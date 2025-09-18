import logging
import sys
from typing import Optional


def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_app_logger(log_file: str = "app.log"):
    return setup_logger("chirp-api", "INFO", log_file)


def log_request(logger, method: str, endpoint: str, status_code: Optional[int] = None):
    if status_code:
        logger.info(f"{method} {endpoint} - {status_code}")
    else:
        logger.info(f"{method} {endpoint}")


def log_error(logger, error: Exception, context: str = ""):
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True)