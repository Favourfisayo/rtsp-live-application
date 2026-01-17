"""Shared utility functions for API controllers."""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def error_response(message: str, status_code: int) -> Tuple[Dict[str, str], int]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message to return to client (should be sanitized)
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    return {"error": message}, status_code


def sanitize_error_message(error: Exception, default_message: str = "An error occurred") -> str:
    """
    Sanitize error messages to prevent information leakage.
    
    Logs the full error internally but returns a generic message to clients.
    
    Args:
        error: The exception that occurred
        default_message: The generic message to return to clients
        
    Returns:
        Sanitized error message safe for client exposure
    """
    # Log detailed error internally
    logger.error(f"Error occurred: {type(error).__name__}: {str(error)}", exc_info=True)
    
    # Return generic message to client
    return default_message


def validate_id_parameter(id_param: str) -> bool:
    """
    Validate that an ID parameter is safe and well-formed.
    
    """
    if not id_param or not isinstance(id_param, str):
        return False
    
    # Check length (MongoDB ObjectIds are 24 characters)
    if len(id_param) > 100:
        return False
    
    # Check for obviously malicious patterns
    forbidden_chars = ['$', '{', '}', '<', '>', ';', '|', '&']
    return not any(char in id_param for char in forbidden_chars)

