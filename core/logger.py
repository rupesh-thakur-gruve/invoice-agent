
import logging
import sys
from core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance.
    Logs are directed to stdout to be captured by Docker.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger is already configured
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(settings.LOG_LEVEL)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
    return logger
