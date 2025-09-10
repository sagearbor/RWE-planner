import logging
import sys
from datetime import datetime
import json
from typing import Any, Dict

class StructuredLogger:
    """Structured logger for consistent logging across all services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create console handler with structured format
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Use JSON format for structured logging
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def _format_message(self, level: str, message: str, **kwargs) -> str:
        """Format log message as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry)
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message("INFO", message, **kwargs))
    
    def error(self, message: str, error: Exception = None, **kwargs):
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
        self.logger.error(self._format_message("ERROR", message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message("WARNING", message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message("DEBUG", message, **kwargs))
    
    def log_request(self, endpoint: str, method: str, duration_ms: float, status_code: int, **kwargs):
        """Log API request with metrics"""
        self.info(
            "API request completed",
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
            **kwargs
        )
    
    def log_dependency(self, service: str, endpoint: str, duration_ms: float, success: bool, **kwargs):
        """Log external service dependency call"""
        self.info(
            "Dependency call",
            dependency_service=service,
            endpoint=endpoint,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )