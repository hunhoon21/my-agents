import sys
from loguru import logger
from typing import Optional, Any


def get_logger(name: Optional[str] = None) -> Any:
    if name:
        return logger.bind(component=name)
    return logger


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    logger.remove()

    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[component]: <20}</cyan> | <level>{message}</level>",
        colorize=True,
    )

    if log_file:
        logger.add(
            log_file,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[component]: <20} | {message}",
            rotation="10 MB",
            retention="30 days",
        )
