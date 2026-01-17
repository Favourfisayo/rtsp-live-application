"""Overlay Service - Business logic for overlay CRUD operations."""

import base64
import html
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, List, Optional

import requests

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

from my_app_db.models import Overlay


class ImageDownloadError(Exception):
    """Raised when image download fails."""
    pass


class ImageDownloader:
    """Downloads images from URLs and converts them to base64 data URLs."""
    
    TIMEOUT = 10
    MAX_SIZE = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = ('image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml')
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    }
    
    @classmethod
    def download_and_encode(cls, url: str) -> str:
        """Download an image from URL and convert it to a base64 data URL."""
        if not url or not url.startswith(('http://', 'https://')):
            raise ImageDownloadError(f"Invalid image URL: {url}")
        
        try:
            response = requests.get(url, timeout=cls.TIMEOUT, stream=True, headers=cls.HEADERS, allow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            if not any(ct in content_type for ct in cls.ALLOWED_CONTENT_TYPES):
                raise ImageDownloadError(f"Invalid content type: {content_type}. Expected image.")
            
            content = BytesIO()
            size = 0
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
                if size > cls.MAX_SIZE:
                    raise ImageDownloadError(f"Image too large (max {cls.MAX_SIZE} bytes)")
                content.write(chunk)
            
            image_data = content.getvalue()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            main_content_type = content_type.split(';')[0].strip()
            
            return f"data:{main_content_type};base64,{base64_data}"
            
        except requests.RequestException as e:
            raise ImageDownloadError(f"Failed to download image: {str(e)}") from e


class ContentSanitizer:
    """Sanitizes user content to prevent XSS attacks."""
    
    # Patterns that indicate potential XSS attacks
    DANGEROUS_PATTERNS = (
        re.compile(r'<script[^>]*>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick=, onerror=, etc.
        re.compile(r'<iframe[^>]*>', re.IGNORECASE),
        re.compile(r'<object[^>]*>', re.IGNORECASE),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
    )
    
    @classmethod
    def sanitize(cls, content: str) -> str:
        """Remove potentially dangerous HTML/script content."""
        if not content:
            return content
        
        if BLEACH_AVAILABLE:
            # Use bleach for comprehensive sanitization
            sanitized = bleach.clean(content, tags=[], strip=True)
        else:
            # Fallback: manual sanitization if bleach not available
            sanitized = cls._manual_sanitize(content)
        
        # Additionally strip javascript: protocol 
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        return sanitized
    
    @classmethod
    def _manual_sanitize(cls, content: str) -> str:
        """Fallback sanitization without bleach."""

        sanitized = html.escape(content)
        return sanitized
    
    @classmethod
    def is_safe(cls, content: str) -> bool:
        """Check if content contains dangerous patterns."""
        if not content:
            return True
        
        return all(not pattern.search(content) for pattern in cls.DANGEROUS_PATTERNS)


@dataclass
class OverlayData:
    type: str
    content: str
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 100.0
    z_index: int = 1
    visible: bool = True
    image_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], sanitize: bool = True) -> 'OverlayData':
        content = data.get('content', '')
        overlay_type = data.get('type', '')
        image_url = None
        
        if sanitize and overlay_type == 'text':
            content = ContentSanitizer.sanitize(content)
        
        if overlay_type == 'image':
            image_url = content
            content = ImageDownloader.download_and_encode(content)
        
        return cls(
            type=overlay_type,
            content=content,
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            width=data.get('width', 100.0),
            height=data.get('height', 100.0),
            z_index=data.get('zIndex', 1),
            visible=data.get('visible', True),
            image_url=image_url
        )


class OverlayRepository(ABC):
    @abstractmethod
    def create(self, data: OverlayData) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def find_by_id(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update(self, overlay_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete(self, overlay_id: str) -> bool:
        pass


class OverlayResponseFormatter:
    """Transforms MongoDB overlay documents into API response format."""
    
    ALLOWED_UPDATE_FIELDS = frozenset(['type', 'content', 'imageUrl', 'x', 'y', 'width', 'height', 'zIndex', 'visible'])
    
    @staticmethod
    def format(overlay_dict: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not overlay_dict:
            return None
        
        return {
            "_id": OverlayResponseFormatter._extract_id(overlay_dict),
            "type": overlay_dict.get("type"),
            "content": overlay_dict.get("content"),
            "imageUrl": overlay_dict.get("imageUrl"),
            "x": overlay_dict.get("x", 0),
            "y": overlay_dict.get("y", 0),
            "width": overlay_dict.get("width", 100),
            "height": overlay_dict.get("height", 100),
            "zIndex": overlay_dict.get("zIndex", 1),
            "visible": overlay_dict.get("visible", True),
            "created_at": OverlayResponseFormatter._extract_date(overlay_dict, "created_at"),
            "updated_at": OverlayResponseFormatter._extract_date(overlay_dict, "updated_at")
        }
    
    @staticmethod
    def _extract_id(data: Dict[str, Any]) -> str:
        _id = data.get("_id", {})
        if isinstance(_id, dict) and "$oid" in _id:
            return _id["$oid"]
        return str(_id)
    
    @staticmethod
    def _extract_date(data: Dict[str, Any], field: str) -> Any:
        value = data.get(field, {})
        if isinstance(value, dict) and "$date" in value:
            return value["$date"]
        return value


class MongoOverlayRepository(OverlayRepository):
    def __init__(self, formatter: Optional[OverlayResponseFormatter] = None):
        self._formatter = formatter or OverlayResponseFormatter()
    
    def create(self, data: OverlayData) -> Dict[str, Any]:
        overlay = Overlay(
            type=data.type,
            content=data.content,
            imageUrl=data.image_url,
            x=data.x,
            y=data.y,
            width=data.width,
            height=data.height,
            zIndex=data.z_index,
            visible=data.visible
        )
        overlay.save()
        return self._to_formatted_dict(overlay)
    
    def find_all(self) -> List[Dict[str, Any]]:
        overlays = Overlay.objects()
        overlay_list = json.loads(overlays.to_json())
        return [self._formatter.format(o) for o in overlay_list]
    
    def find_by_id(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        overlay = Overlay.objects(id=overlay_id).first()
        if not overlay:
            return None
        return self._to_formatted_dict(overlay)
    
    def update(self, overlay_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        overlay = Overlay.objects(id=overlay_id).first()
        if not overlay:
            return None
        
        for field in OverlayResponseFormatter.ALLOWED_UPDATE_FIELDS:
            if field in data:
                setattr(overlay, field, data[field])
        
        overlay.save()
        return self._to_formatted_dict(overlay)
    
    def delete(self, overlay_id: str) -> bool:
        overlay = Overlay.objects(id=overlay_id).first()
        if not overlay:
            return False
        overlay.delete()
        return True
    
    def _to_formatted_dict(self, overlay: Overlay) -> Dict[str, Any]:
        return self._formatter.format(json.loads(overlay.to_json()))


class OverlayService:
    """Application service for overlay management operations."""
    
    def __init__(self, repository: Optional[OverlayRepository] = None):
        self._repository = repository or MongoOverlayRepository()
    
    def create_overlay(self, data: Dict[str, Any]) -> Dict[str, Any]:
        overlay_data = OverlayData.from_dict(data)
        return self._repository.create(overlay_data)
    
    def get_all_overlays(self) -> List[Dict[str, Any]]:
        return self._repository.find_all()
    
    def get_overlay(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.find_by_id(overlay_id)
    
    def update_overlay(self, overlay_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an overlay, downloading new image if imageUrl changes."""
        if 'imageUrl' in data:
            existing = self._repository.find_by_id(overlay_id)
            if existing and existing.get('type') == 'image':
                new_url = data['imageUrl']
                if new_url and new_url != existing.get('imageUrl'):
                    data['content'] = ImageDownloader.download_and_encode(new_url)
        
        return self._repository.update(overlay_id, data)
    
    def delete_overlay(self, overlay_id: str) -> bool:
        return self._repository.delete(overlay_id)
