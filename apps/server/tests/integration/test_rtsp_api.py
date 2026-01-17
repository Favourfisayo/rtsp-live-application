"""Integration tests for RTSP API endpoints.

Tests cover:
- POST /api/rtsp/connect
- POST /api/rtsp/disconnect
- GET /api/rtsp/status
- Error handling for invalid URLs and connection failures
"""

from unittest.mock import MagicMock, patch


class TestRtspConnectEndpoint:
    """Test suite for POST /api/rtsp/connect endpoint."""
    
    def test_connect_success(self, client):
        """Test successful stream connection."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.connect_stream.return_value = {
                'status': 'live',
                'url': 'rtsp://test-stream/live',
                'streamPath': '/static/hls/stream.m3u8'
            }
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/connect', json={
                'url': 'rtsp://test-stream/live'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'live'
            assert 'streamUrl' in data
    
    def test_connect_with_rtsp_url_field(self, client):
        """Test connect accepts rtsp_url field as alternative."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.connect_stream.return_value = {
                'status': 'live',
                'url': 'rtsp://camera/stream',
                'streamPath': '/static/hls/stream.m3u8'
            }
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/connect', json={
                'rtsp_url': 'rtsp://camera/stream'
            })
            
            assert response.status_code == 200
    
    def test_connect_no_data(self, client):
        """Test connect fails with no JSON data."""
        response = client.post('/api/rtsp/connect')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_connect_no_url(self, client):
        """Test connect fails when URL is missing."""
        response = client.post('/api/rtsp/connect', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'URL' in data['error'] or 'required' in data['error'].lower()
    
    def test_connect_invalid_url_returns_400(self, client):
        """Test connect returns 400 for invalid RTSP URL."""
        from src.modules.rtsp.rtsp_service import StreamValidationError
        
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.connect_stream.side_effect = StreamValidationError(
                'Invalid RTSP URL format'
            )
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/connect', json={
                'url': 'http://not-rtsp'
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_connect_connection_failure_returns_500(self, client):
        """Test connect returns 500 when stream connection fails."""
        from src.modules.rtsp.rtsp_service import StreamConnectionError
        
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.connect_stream.side_effect = StreamConnectionError(
                'Failed to start stream - connection refused'
            )
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/connect', json={
                'url': 'rtsp://unreachable-host/stream'
            })
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data


class TestRtspDisconnectEndpoint:
    """Test suite for POST /api/rtsp/disconnect endpoint."""
    
    def test_disconnect_success(self, client):
        """Test successful stream disconnection."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.disconnect_stream.return_value = {
                'status': 'disconnected'
            }
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/disconnect')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'disconnected'
    
    def test_disconnect_when_no_active_stream(self, client):
        """Test disconnect works even when no stream is active."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.disconnect_stream.return_value = {
                'status': 'disconnected'
            }
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/disconnect')
            
            assert response.status_code == 200


class TestRtspStatusEndpoint:
    """Test suite for GET /api/rtsp/status endpoint."""
    
    def test_status_idle(self, client):
        """Test status when no stream is active."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_status.return_value = {
                'status': 'idle',
                'url': None
            }
            mock_get_service.return_value = mock_service
            
            response = client.get('/api/rtsp/status')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'idle'
    
    def test_status_live(self, client):
        """Test status when stream is active."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_status.return_value = {
                'status': 'live',
                'url': 'rtsp://active-stream/live'
            }
            mock_get_service.return_value = mock_service
            
            response = client.get('/api/rtsp/status')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'live'
            assert data['url'] == 'rtsp://active-stream/live'


class TestRtspApiErrorHandling:
    """Test error handling across RTSP API endpoints."""
    
    def test_connect_injection_attempt_rejected(self, client):
        """Test that injection attempts in URL are rejected."""
        from src.modules.rtsp.rtsp_service import StreamValidationError
        
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.connect_stream.side_effect = StreamValidationError(
                'Invalid RTSP URL format'
            )
            mock_get_service.return_value = mock_service
            
            response = client.post('/api/rtsp/connect', json={
                'url': 'rtsp://example.com;rm -rf /'
            })
            
            assert response.status_code == 400
    
    def test_connect_empty_url_rejected(self, client):
        """Test that empty URL is rejected."""
        response = client.post('/api/rtsp/connect', json={
            'url': ''
        })
        
        assert response.status_code == 400
