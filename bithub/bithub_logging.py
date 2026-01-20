"""
Why: Centralizes logging configuration to ensure consistency and optionality.
What: Provides a setup function to configure JSON or console logging.
How: Uses Python's logging module with a custom JSON formatter.
"""

import logging
import json
import os
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Formatter that outputs JSON strings."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        # Add correlation ID if present in record
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        return json.dumps(log_record)

def configure_logging():
    """Configures the root logger based on environment variables.
    
    Defaults to WARNING level (quiet). 
    If BITHUB_DEBUG=1, switches to DEBUG level and JSON format.
    """
    debug_mode = os.environ.get("BITHUB_DEBUG", "0") == "1"
    
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        handler.setFormatter(JsonFormatter())
    else:
        logger.setLevel(logging.WARNING)
        # Simple format for errors when not in debug mode
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)
