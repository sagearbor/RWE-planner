from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any
import traceback
from .logger import StructuredLogger

class ErrorHandler:
    """Centralized error handling for all services"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler"""
        
        # Log the full error with traceback
        self.logger.error(
            "Unhandled exception",
            error=exc,
            path=str(request.url),
            method=request.method,
            traceback=traceback.format_exc()
        )
        
        # Determine appropriate response
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "path": str(request.url)
                }
            )
        elif isinstance(exc, ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "error": str(exc),
                    "status_code": 400,
                    "path": str(request.url)
                }
            )
        else:
            # Generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "status_code": 500,
                    "path": str(request.url),
                    "detail": str(exc) if request.app.debug else None
                }
            )
    
    def validate_request(self, data: dict, required_fields: list) -> None:
        """Validate required fields in request"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    def handle_service_error(self, service_name: str, error: Exception) -> None:
        """Handle errors from external service calls"""
        self.logger.error(
            f"Service call failed: {service_name}",
            error=error,
            service=service_name
        )
        
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} is unavailable: {str(error)}"
        )

class ServiceHealthChecker:
    """Health check utilities for services"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.healthy = True
        self.last_error = None
    
    def set_unhealthy(self, reason: str):
        """Mark service as unhealthy"""
        self.healthy = False
        self.last_error = reason
        self.logger.error(f"Service marked unhealthy: {reason}")
    
    def set_healthy(self):
        """Mark service as healthy"""
        self.healthy = True
        self.last_error = None
        self.logger.info("Service marked healthy")
    
    def get_health_status(self) -> dict:
        """Get current health status"""
        return {
            "healthy": self.healthy,
            "status": "healthy" if self.healthy else "unhealthy",
            "error": self.last_error
        }