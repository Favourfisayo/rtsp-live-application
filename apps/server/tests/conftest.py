"""
Pytest configuration and fixtures for RTSP Overlay Backend tests.

Provides:
- Flask test client fixture
- MongoDB mock setup with mongomock
- Service fixtures with dependency injection
- Mock fixtures for FFmpegManager and repositories
"""

import os
import sys
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))



@pytest.fixture(scope='session', autouse=True)
def mock_mongoengine():
    """Mock mongoengine to use mongomock for all tests."""
    import mongomock
    
    with patch('mongoengine.connect') as mock_connect:
        mock_connect.return_value = mongomock.MongoClient()
        yield mock_connect


@pytest.fixture(scope='function')
def mock_db():
    """Provide a fresh mongomock database for each test."""
    import mongomock
    client = mongomock.MongoClient()
    db = client['test_database']
    yield db
    # Cleanup after each test
    client.drop_database('test_database')


@pytest.fixture(scope='function')
def app(mock_mongoengine):
    """Create Flask test application with registered blueprints."""
    from flask import Flask

    from src.modules.overlays.overlay_controller import overlay_bp
    from src.modules.rtsp.rtsp_controller import rtsp_bp
    
    test_app = Flask(__name__, static_folder='../static')
    test_app.config['TESTING'] = True
    test_app.config['MONGODB_SETTINGS'] = {
        'host': 'mongomock://localhost',
        'db': 'test_database'
    }
    
    test_app.register_blueprint(rtsp_bp)
    test_app.register_blueprint(overlay_bp)
    
    @test_app.route('/')
    def health():
        return '<p>RTSP Overlay Backend Running</p>'
    
    yield test_app


@pytest.fixture(scope='function')
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """Provide application context for tests."""
    with app.app_context():
        yield


# --- RTSP Fixtures ---

@pytest.fixture
def rtsp_validator():
    """Provide RtspUrlValidator instance."""
    from src.validators.rtsp_validators import RtspUrlValidator
    return RtspUrlValidator()


# --- Mock Stream Manager Fixtures ---

@pytest.fixture
def mock_stream_manager():
    """Mock StreamManager in idle state."""
    manager = MagicMock()
    manager.start.return_value = True
    manager.stop.return_value = None
    manager.get_status.return_value = 'idle'
    manager.get_current_url.return_value = None
    manager.get_last_error.return_value = None
    return manager


@pytest.fixture
def mock_stream_manager_live():
    """Mock StreamManager in live streaming state."""
    manager = MagicMock()
    manager.start.return_value = True
    manager.stop.return_value = None
    manager.get_status.return_value = 'live'
    manager.get_current_url.return_value = 'rtsp://test-stream/live'
    manager.get_last_error.return_value = None
    return manager


@pytest.fixture
def mock_stream_manager_failing():
    """Mock StreamManager that fails to connect."""
    manager = MagicMock()
    manager.start.return_value = False
    manager.get_last_error.return_value = 'Connection refused'
    return manager


# --- RTSP Service Fixtures ---

@pytest.fixture
def rtsp_service(mock_stream_manager, tmp_path):
    """RtspService with mocked idle stream manager."""
    from src.modules.rtsp.rtsp_service import RtspService
    return RtspService(static_folder=str(tmp_path), stream_manager=mock_stream_manager)


@pytest.fixture
def rtsp_service_live(mock_stream_manager_live, tmp_path):
    """RtspService with active live stream."""
    from src.modules.rtsp.rtsp_service import RtspService
    return RtspService(static_folder=str(tmp_path), stream_manager=mock_stream_manager_live)


@pytest.fixture
def rtsp_service_failing(mock_stream_manager_failing, tmp_path):
    """RtspService that fails on connection."""
    from src.modules.rtsp.rtsp_service import RtspService
    return RtspService(static_folder=str(tmp_path), stream_manager=mock_stream_manager_failing)


# --- Mock Overlay Repository ---

class MockOverlayRepository:
    """In-memory overlay repository for testing."""
    
    def __init__(self):
        self._overlays: Dict[str, Dict[str, Any]] = {}
        self._id_counter = 0
    
    def create(self, data) -> Dict[str, Any]:
        self._id_counter += 1
        overlay_id = str(self._id_counter)
        overlay = {
            '_id': overlay_id,
            'type': data.type,
            'content': data.content,
            'x': data.x,
            'y': data.y,
            'width': data.width,
            'height': data.height,
            'zIndex': data.z_index,
            'visible': data.visible,
            'created_at': '2026-01-16T00:00:00Z',
            'updated_at': '2026-01-16T00:00:00Z'
        }
        self._overlays[overlay_id] = overlay
        return overlay.copy()
    
    def find_all(self) -> List[Dict[str, Any]]:
        return [o.copy() for o in self._overlays.values()]
    
    def find_by_id(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        overlay = self._overlays.get(overlay_id)
        return overlay.copy() if overlay else None
    
    def update(self, overlay_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if overlay_id not in self._overlays:
            return None
        
        allowed_fields = {'type', 'content', 'x', 'y', 'width', 'height', 'zIndex', 'visible'}
        for field in allowed_fields:
            if field in data:
                self._overlays[overlay_id][field] = data[field]
        
        self._overlays[overlay_id]['updated_at'] = '2026-01-16T00:00:01Z'
        return self._overlays[overlay_id].copy()
    
    def delete(self, overlay_id: str) -> bool:
        if overlay_id not in self._overlays:
            return False
        del self._overlays[overlay_id]
        return True
    
    def clear(self):
        """Clear all overlays - useful for test cleanup."""
        self._overlays.clear()
        self._id_counter = 0


@pytest.fixture
def mock_overlay_repository():
    """Fresh MockOverlayRepository for each test."""
    return MockOverlayRepository()


# --- Overlay Service Fixtures ---

@pytest.fixture
def overlay_service(mock_overlay_repository):
    """OverlayService with mocked repository."""
    from src.modules.overlays.overlay_service import OverlayService
    return OverlayService(repository=mock_overlay_repository)


# --- Sample Data Fixtures ---

@pytest.fixture
def valid_rtsp_urls():
    """Valid RTSP URLs for testing."""
    return [
        'rtsp://192.168.1.100:554/stream',
        'rtsp://camera.example.com/live',
        'rtsp://user:pass@192.168.1.100/stream',
        'rtsp://localhost/test',
        'rtsp://10.0.0.1:8554/video',
    ]


@pytest.fixture
def invalid_rtsp_urls():
    """Invalid RTSP URLs including injection attempts."""
    return [
        '',
        'http://example.com/stream',
        'https://example.com/stream',
        'ftp://example.com/file',
        'rtsp://',
        'not-a-url',
        'rtsp://example.com;rm -rf /',
        'rtsp://example.com|cat /etc/passwd',
        'rtsp://example.com`whoami`',
        'rtsp://example.com$(id)',
    ]


@pytest.fixture
def sample_text_overlay_data():
    """Sample text overlay data."""
    return {
        'type': 'text',
        'content': 'Hello World',
        'x': 50.0,
        'y': 100.0,
        'width': 200.0,
        'height': 50.0,
        'zIndex': 1,
        'visible': True
    }


@pytest.fixture
def sample_image_overlay_data():
    """Sample image overlay data."""
    return {
        'type': 'image',
        'content': 'https://example.com/logo.png',
        'x': 10.0,
        'y': 10.0,
        'width': 100.0,
        'height': 100.0,
        'zIndex': 2,
        'visible': True
    }


@pytest.fixture
def xss_payloads():
    """XSS attack payloads for security testing."""
    return [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        '<svg onload=alert("XSS")>',
        'javascript:alert("XSS")',
        '<iframe src="javascript:alert(\'XSS\')">',
        '<body onload=alert("XSS")>',
        '"><script>alert("XSS")</script>',
        "'-alert('XSS')-'",
        '<a href="javascript:alert(\'XSS\')">click</a>',
    ]
