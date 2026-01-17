"""Unit tests for RTSP Service."""

from unittest.mock import MagicMock

import pytest

from src.modules.rtsp.rtsp_service import (
    FFmpegStreamManager,
    RtspService,
    StreamConnectionError,
    StreamResponse,
    StreamValidationError,
)

# --- StreamResponse Dataclass Tests ---

class TestStreamResponse:
    """Tests for StreamResponse dataclass serialization."""
    
    def test_to_dict_minimal(self):
        response = StreamResponse(status='idle')
        result = response.to_dict()
        
        assert result == {'status': 'idle'}
        assert 'url' not in result
        assert 'streamPath' not in result
    
    def test_to_dict_with_url(self):
        response = StreamResponse(status='live', url='rtsp://test')
        result = response.to_dict()
        
        assert result['status'] == 'live'
        assert result['url'] == 'rtsp://test'
        assert 'streamPath' not in result
    
    def test_to_dict_full(self):
        response = StreamResponse(
            status='live',
            url='rtsp://test',
            stream_path='/static/hls/stream.m3u8'
        )
        result = response.to_dict()
        
        assert result['status'] == 'live'
        assert result['url'] == 'rtsp://test'
        assert result['streamPath'] == '/static/hls/stream.m3u8'


# --- Connect Stream Tests ---

class TestRtspServiceConnectStream:
    """Tests for RtspService.connect_stream - success and error paths."""
    
    def test_connect_stream_success(self, rtsp_service, mock_stream_manager):
        result = rtsp_service.connect_stream('rtsp://valid-stream/live')
        
        assert result['status'] == 'live'
        assert result['url'] == 'rtsp://valid-stream/live'
        assert 'streamPath' in result
        mock_stream_manager.start.assert_called_once()
    
    def test_connect_stream_returns_stream_path(self, rtsp_service):
        result = rtsp_service.connect_stream('rtsp://camera/stream')
        assert result['streamPath'] == '/static/hls/stream.m3u8'
    
    def test_connect_stream_invalid_url_raises_validation_error(self, rtsp_service):
        with pytest.raises(StreamValidationError) as exc_info:
            rtsp_service.connect_stream('http://not-rtsp/stream')
        assert 'Invalid RTSP URL' in str(exc_info.value)
    
    def test_connect_stream_empty_url_raises_validation_error(self, rtsp_service):
        with pytest.raises(StreamValidationError):
            rtsp_service.connect_stream('')
    
    def test_connect_stream_injection_url_raises_validation_error(self, rtsp_service):
        with pytest.raises(StreamValidationError):
            rtsp_service.connect_stream('rtsp://example.com;rm -rf /')
    
    def test_connect_stream_ffmpeg_failure_raises_connection_error(self, rtsp_service_failing):
        with pytest.raises(StreamConnectionError) as exc_info:
            rtsp_service_failing.connect_stream('rtsp://valid-but-unreachable/stream')
        assert 'Failed to start stream' in str(exc_info.value)
    
    def test_connect_stream_includes_ffmpeg_error_in_exception(self, rtsp_service_failing):
        with pytest.raises(StreamConnectionError) as exc_info:
            rtsp_service_failing.connect_stream('rtsp://unreachable/stream')
        assert 'Connection refused' in str(exc_info.value)


# --- Disconnect Stream Tests ---

class TestRtspServiceDisconnectStream:
    """Tests for RtspService.disconnect_stream."""
    
    def test_disconnect_stream_success(self, rtsp_service_live, mock_stream_manager_live):
        result = rtsp_service_live.disconnect_stream()
        
        assert result['status'] == 'disconnected'
        mock_stream_manager_live.stop.assert_called_once()
    
    def test_disconnect_stream_when_idle(self, rtsp_service, mock_stream_manager):
        result = rtsp_service.disconnect_stream()
        
        assert result['status'] == 'disconnected'
        mock_stream_manager.stop.assert_called_once()


# --- Get Status Tests ---

class TestRtspServiceGetStatus:
    """Tests for RtspService.get_status."""
    
    def test_get_status_idle(self, rtsp_service, mock_stream_manager):
        result = rtsp_service.get_status()
        
        assert result['status'] == 'idle'
        assert result['url'] is None
    
    def test_get_status_live(self, rtsp_service_live, mock_stream_manager_live):
        result = rtsp_service_live.get_status()
        
        assert result['status'] == 'live'
        assert result['url'] == 'rtsp://test-stream/live'


# --- Custom Validator Injection Tests ---

class TestRtspServiceWithCustomValidator:
    """Tests for RtspService with injected validators."""
    
    def test_custom_validator_rejects(self, mock_stream_manager, tmp_path):
        strict_validator = MagicMock()
        strict_validator.is_valid.return_value = False
        
        service = RtspService(
            static_folder=str(tmp_path),
            stream_manager=mock_stream_manager,
            validator=strict_validator
        )
        
        with pytest.raises(StreamValidationError):
            service.connect_stream('rtsp://should-fail')
        
        strict_validator.is_valid.assert_called_once_with('rtsp://should-fail')
    
    def test_custom_validator_allows_connection(self, mock_stream_manager, tmp_path):
        permissive_validator = MagicMock()
        permissive_validator.is_valid.return_value = True
        
        service = RtspService(
            static_folder=str(tmp_path),
            stream_manager=mock_stream_manager,
            validator=permissive_validator
        )
        
        result = service.connect_stream('rtsp://any-url')
        assert result['status'] == 'live'


# --- FFmpegStreamManager Interface Tests ---

class TestFFmpegStreamManagerInterface:
    """Tests verifying FFmpegStreamManager implements StreamManager interface."""
    
    def test_has_start_method(self):
        manager = FFmpegStreamManager()
        assert hasattr(manager, 'start') and callable(manager.start)
    
    def test_has_stop_method(self):
        manager = FFmpegStreamManager()
        assert hasattr(manager, 'stop') and callable(manager.stop)
    
    def test_has_get_status_method(self):
        manager = FFmpegStreamManager()
        assert hasattr(manager, 'get_status') and callable(manager.get_status)
    
    def test_has_get_current_url_method(self):
        manager = FFmpegStreamManager()
        assert hasattr(manager, 'get_current_url') and callable(manager.get_current_url)
    
    def test_has_get_last_error_method(self):
        manager = FFmpegStreamManager()
        assert hasattr(manager, 'get_last_error') and callable(manager.get_last_error)
