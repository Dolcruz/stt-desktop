import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import get_app_dir


def configure_logging() -> Path:
    """Configure application logging to a rotating file under AppData.

    Returns the path to the log file.
    """
    log_dir = get_app_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for development
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(file_formatter)
    logger.addHandler(console)

    logging.getLogger("sounddevice").setLevel(logging.WARNING)

    return log_path
