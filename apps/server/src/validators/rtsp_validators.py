"""RTSP URL Validation - Validates RTSP protocol URLs with security checks."""

import re
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import ParseResult, urlparse


class UrlValidator(ABC):
    @abstractmethod
    def is_valid(self, url: str) -> bool:
        pass


class RtspUrlValidator(UrlValidator):
    """
    Validates RTSP URLs ensuring proper format and blocking injection attempts.
    
    Valid format: rtsp://[username:password@]host[:port]/path
    Uses urllib.parse for robust URL parsing and validation.
    """
    
    RTSP_PATTERN = re.compile(r'^rtsp://[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]+$')
    FORBIDDEN_SEQUENCES = (';', '|', '`', '$', '&', '>', '<', '\n', '\r', '\\')
    MAX_URL_LENGTH = 2048
    VALID_SCHEMES = {'rtsp', 'rtsps'}
    
    def is_valid(self, url: str) -> bool:
        """
        Validate RTSP URL with multiple security checks.
        Returns True if URL is valid and safe, False otherwise.
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check URL length to prevent buffer overflow attempts
        if len(url) > self.MAX_URL_LENGTH:
            return False
        
        # Check for injection sequences
        if self._contains_injection_sequences(url):
            return False
        
        # Basic pattern check
        if not self.RTSP_PATTERN.match(url):
            return False
        
        # Parse URL structure
        parsed = self._parse_url(url)
        if not parsed:
            return False
        
        # Validate scheme
        if parsed.scheme not in self.VALID_SCHEMES:
            return False
        
        # Validate hostname exists
        if not parsed.hostname:
            return False
        
        # Validate port if present
        return not (parsed.port is not None and not 1 <= parsed.port <= 65535)
    
    def _parse_url(self, url: str) -> Optional[ParseResult]:
        """
        Parse URL using urllib.parse for robust validation.
        Returns ParseResult if valid, None otherwise.
        """
        try:
            parsed = urlparse(url)
            return parsed
        except Exception:
            return None
    
    def _contains_injection_sequences(self, url: str) -> bool:
        """Check for command injection sequences."""
        return any(seq in url for seq in self.FORBIDDEN_SEQUENCES)


def validate_rtsp_url(url: str) -> bool:
    """Convenience function for backward compatibility."""
    return RtspUrlValidator().is_valid(url)
