"""
Custom exceptions for RFP Automation System
Provides structured error handling with proper HTTP status codes
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class RFPException(Exception):
    """Base exception for RFP Automation System"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(RFPException):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class AuthenticationError(RFPException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(RFPException):
    """Raised when user lacks permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(RFPException):
    """Raised when resource is not found"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )


class ConflictError(RFPException):
    """Raised when resource conflicts with existing data"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(RFPException):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after}
        )


class ExternalServiceError(RFPException):
    """Raised when external service (LLM, etc.) fails"""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"service": service}
        )


class DatabaseError(RFPException):
    """Raised when database operation fails"""
    def __init__(self, message: str, operation: str):
        super().__init__(
            message=f"Database error during {operation}: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation}
        )


def handle_exception(exc: Exception) -> HTTPException:
    """Convert custom exceptions to HTTPException with proper logging"""
    if isinstance(exc, RFPException):
        logger.error(f"RFPException: {exc.message}", exc_info=True)
        return HTTPException(
            status_code=exc.status_code,
            detail={
                "error": True,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    # Handle unexpected exceptions
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": True,
            "message": "Internal server error",
            "details": {"type": type(exc).__name__}
        }
    )


def create_error_response(message: str, status_code: int, details: Optional[Dict] = None) -> HTTPException:
    """Create standardized error response"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": True,
            "message": message,
            "details": details or {}
        }
    )
