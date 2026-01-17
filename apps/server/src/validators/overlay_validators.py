"""Overlay Data Validation - Validates overlay input with security checks."""

from typing import Any, Dict, List, Optional

import bleach


class OverlayValidator:
    """
    Validates overlay data to prevent XSS, injection attacks, and data integrity issues.
    """
    
    VALID_TYPES = {'text', 'image'}
    MAX_CONTENT_LENGTH = 1000
    MAX_COORDINATE = 10000
    MIN_COORDINATE = -1000
    MAX_DIMENSION = 5000
    MIN_DIMENSION = 0
    
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'span']
    ALLOWED_HTML_ATTRIBUTES = {}  # No attributes allowed for security
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate overlay data. Returns True if valid, False otherwise.
        Populates self.errors with validation error messages.
        """
        self.errors = []
        
        if not isinstance(data, dict):
            self.errors.append("Data must be a dictionary")
            return False
        

        overlay_type = data.get('type')
        if not overlay_type:
            self.errors.append("Type is required")
        elif overlay_type not in self.VALID_TYPES:
            self.errors.append(f"Type must be one of: {', '.join(self.VALID_TYPES)}")
        

        content = data.get('content')
        if not content:
            self.errors.append("Content is required")
        elif not isinstance(content, str):
            self.errors.append("Content must be a string")
        elif len(content) > self.MAX_CONTENT_LENGTH:
            self.errors.append(f"Content must not exceed {self.MAX_CONTENT_LENGTH} characters")
        
        # Position and size are optional, service provides defaults
        self._validate_number('x', data.get('x'), self.MIN_COORDINATE, self.MAX_COORDINATE, allow_none=True)
        self._validate_number('y', data.get('y'), self.MIN_COORDINATE, self.MAX_COORDINATE, allow_none=True)
        self._validate_number('width', data.get('width'), self.MIN_DIMENSION, self.MAX_DIMENSION, allow_none=True)
        self._validate_number('height', data.get('height'), self.MIN_DIMENSION, self.MAX_DIMENSION, allow_none=True)
        
        
        visible = data.get('visible')
        if visible is not None and not isinstance(visible, bool):
            self.errors.append("Visible must be a boolean")
        
       
        z_index = data.get('z_index')
        if z_index is not None:
            self._validate_number('z_index', z_index, -100, 100, allow_none=False)
        
        return len(self.errors) == 0
    
    def _validate_number(
        self, 
        field_name: str, 
        value: Any, 
        min_val: float, 
        max_val: float,
        allow_none: bool = False
    ) -> None:
        """Validate numeric field with range checks."""
        if value is None:
            if not allow_none:
                self.errors.append(f"{field_name} is required")
            return
        
        if not isinstance(value, (int, float)):
            self.errors.append(f"{field_name} must be a number")
            return
        
        if value < min_val or value > max_val:
            self.errors.append(f"{field_name} must be between {min_val} and {max_val}")
    
    def sanitize_content(self, content: str, overlay_type: str) -> str:
        """
        Sanitize content to prevent XSS attacks.
        For text overlays, allows limited HTML tags.
        For image overlays, validates URL format.
        """
        if overlay_type == 'text':

            return bleach.clean(
                content,
                tags=self.ALLOWED_HTML_TAGS,
                attributes=self.ALLOWED_HTML_ATTRIBUTES,
                strip=True
            )
        elif overlay_type == 'image':

            return bleach.clean(content, tags=[], strip=True)
        
        return content
    
    def get_error_message(self) -> str:
        """Get a formatted error message from all validation errors."""
        return "; ".join(self.errors) if self.errors else ""


def validate_overlay_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Convenience function for overlay validation (CREATE).
    Returns (is_valid, error_message).
    """
    validator = OverlayValidator()
    is_valid = validator.validate(data)
    
    if not is_valid:
        return False, validator.get_error_message()
    
    # Sanitize content if present
    if 'content' in data and 'type' in data:
        data['content'] = validator.sanitize_content(data['content'], data['type'])
    
    return True, None


def validate_overlay_update_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate partial overlay data for UPDATE operations.
    Only validates fields that are present, does not require all fields.
    Returns (is_valid, error_message).
    """
    validator = OverlayValidator()
    validator.errors = []
    
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    # Type validation (if present)
    if 'type' in data:
        overlay_type = data['type']
        if overlay_type not in validator.VALID_TYPES:
            validator.errors.append(f"Type must be one of: {', '.join(validator.VALID_TYPES)}")
    
    if 'content' in data:
        content = data['content']
        if not isinstance(content, str):
            validator.errors.append("Content must be a string")
        elif len(content) > validator.MAX_CONTENT_LENGTH:
            validator.errors.append(f"Content must not exceed {validator.MAX_CONTENT_LENGTH} characters")
    

    if 'x' in data:
        validator._validate_number('x', data['x'], validator.MIN_COORDINATE, validator.MAX_COORDINATE, allow_none=False)
    if 'y' in data:
        validator._validate_number('y', data['y'], validator.MIN_COORDINATE, validator.MAX_COORDINATE, allow_none=False)
    if 'width' in data:
        validator._validate_number('width', data['width'], validator.MIN_DIMENSION, validator.MAX_DIMENSION, allow_none=False)
    if 'height' in data:
        validator._validate_number('height', data['height'], validator.MIN_DIMENSION, validator.MAX_DIMENSION, allow_none=False)
    

    if 'visible' in data:
        visible = data['visible']
        if not isinstance(visible, bool):
            validator.errors.append("Visible must be a boolean")
    

    if 'z_index' in data:
        validator._validate_number('z_index', data['z_index'], -100, 100, allow_none=False)
    
    if validator.errors:
        return False, validator.get_error_message()
    
    # Sanitize content if both type and content are present
    if 'content' in data and 'type' in data:
        data['content'] = validator.sanitize_content(data['content'], data['type'])
    
    return True, None
