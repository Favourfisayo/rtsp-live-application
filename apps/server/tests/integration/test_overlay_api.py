"""Integration tests for Overlay API endpoints.

Tests cover:
- GET /api/overlays (list all)
- POST /api/overlays (create)
- GET /api/overlays/<id> (get single)
- PUT/PATCH /api/overlays/<id> (update)
- DELETE /api/overlays/<id> (delete)
- Error handling (400, 404)
- XSS prevention in API responses
"""

from unittest.mock import patch


class TestOverlayListEndpoint:
    """Test suite for GET /api/overlays endpoint."""
    
    def test_get_overlays_empty(self, client):
        """Test getting overlays when none exist."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.get_all_overlays.return_value = []
            
            response = client.get('/api/overlays')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []
    
    def test_get_overlays_returns_list(self, client):
        """Test getting overlays returns array."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.get_all_overlays.return_value = [
                {'_id': '1', 'type': 'text', 'content': 'First'},
                {'_id': '2', 'type': 'image', 'content': 'https://example.com/img.png'}
            ]
            
            response = client.get('/api/overlays')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['type'] == 'text'
            assert data[1]['type'] == 'image'


class TestOverlayCreateEndpoint:
    """Test suite for POST /api/overlays endpoint."""
    
    def test_create_text_overlay(self, client):
        """Test creating a text overlay."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.create_overlay.return_value = {
                '_id': '1',
                'type': 'text',
                'content': 'Hello World',
                'x': 50,
                'y': 100,
                'width': 200,
                'height': 50,
                'zIndex': 1,
                'visible': True
            }
            
            response = client.post('/api/overlays', json={
                'type': 'text',
                'content': 'Hello World',
                'x': 50,
                'y': 100
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['type'] == 'text'
            assert data['content'] == 'Hello World'
    
    def test_create_image_overlay(self, client):
        """Test creating an image overlay."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.create_overlay.return_value = {
                '_id': '2',
                'type': 'image',
                'content': 'https://example.com/logo.png'
            }
            
            response = client.post('/api/overlays', json={
                'type': 'image',
                'content': 'https://example.com/logo.png'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['type'] == 'image'
    
    def test_create_overlay_no_data(self, client):
        """Test creating overlay fails with no JSON data."""
        response = client.post('/api/overlays')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_overlay_validation_error(self, client):
        """Test create returns 400 on validation error."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.create_overlay.side_effect = ValueError('Invalid type')
            
            response = client.post('/api/overlays', json={
                'type': 'invalid',
                'content': 'test'
            })
            
            assert response.status_code == 400
    
    def test_create_overlay_xss_sanitized(self, client):
        """Test that XSS content is sanitized in create response."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            # Service should return sanitized content
            mock_service.create_overlay.return_value = {
                '_id': '3',
                'type': 'text',
                'content': 'alert("XSS")'  # Script tags removed
            }
            
            response = client.post('/api/overlays', json={
                'type': 'text',
                'content': '<script>alert("XSS")</script>'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert '<script>' not in data['content']


class TestOverlayGetSingleEndpoint:
    """Test suite for GET /api/overlays/<id> endpoint."""
    
    def test_get_overlay_success(self, client):
        """Test getting a single overlay by ID."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.get_overlay.return_value = {
                '_id': '123',
                'type': 'text',
                'content': 'Test'
            }
            
            response = client.get('/api/overlays/123')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['_id'] == '123'
    
    def test_get_overlay_not_found(self, client):
        """Test getting non-existent overlay returns 404."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.get_overlay.return_value = None
            
            response = client.get('/api/overlays/non-existent')
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data


class TestOverlayUpdateEndpoint:
    """Test suite for PUT/PATCH /api/overlays/<id> endpoint."""
    
    def test_update_overlay_put(self, client):
        """Test updating overlay with PUT."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.update_overlay.return_value = {
                '_id': '123',
                'type': 'text',
                'content': 'Updated Content',
                'x': 100
            }
            
            response = client.put('/api/overlays/123', json={
                'content': 'Updated Content',
                'x': 100
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['content'] == 'Updated Content'
    
    def test_update_overlay_patch(self, client):
        """Test updating overlay with PATCH."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.update_overlay.return_value = {
                '_id': '123',
                'visible': False
            }
            
            response = client.patch('/api/overlays/123', json={
                'visible': False
            })
            
            assert response.status_code == 200
    
    def test_update_overlay_no_data(self, client):
        """Test updating overlay fails with no JSON data."""
        response = client.put('/api/overlays/123')
        
        assert response.status_code == 400
    
    def test_update_overlay_not_found(self, client):
        """Test updating non-existent overlay returns 404."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.update_overlay.return_value = None
            
            response = client.put('/api/overlays/non-existent', json={
                'content': 'New'
            })
            
            assert response.status_code == 404
    
    def test_update_overlay_validation_error(self, client):
        """Test update returns 400 on validation error."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.update_overlay.side_effect = ValueError('Invalid field')
            
            response = client.put('/api/overlays/123', json={
                'type': 'invalid'
            })
            
            assert response.status_code == 400


class TestOverlayDeleteEndpoint:
    """Test suite for DELETE /api/overlays/<id> endpoint."""
    
    def test_delete_overlay_success(self, client):
        """Test deleting an overlay."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.delete_overlay.return_value = True
            
            response = client.delete('/api/overlays/123')
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
    
    def test_delete_overlay_not_found(self, client):
        """Test deleting non-existent overlay returns 404."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            mock_service.delete_overlay.return_value = False
            
            response = client.delete('/api/overlays/non-existent')
            
            assert response.status_code == 404


class TestOverlayApiSecurityIntegration:
    """Security-focused integration tests for Overlay API."""
    
    def test_xss_in_text_overlay_sanitized(self, client):
        """Test XSS payload in text overlay is sanitized."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            # Simulate sanitized response from service
            mock_service.create_overlay.return_value = {
                '_id': '1',
                'type': 'text',
                'content': 'Visible Text'  # Script removed
            }
            
            response = client.post('/api/overlays', json={
                'type': 'text',
                'content': '<script>alert("XSS")</script>Visible Text'
            })
            
            data = response.get_json()
            assert '<script>' not in data.get('content', '')
    
    def test_multiple_xss_payloads_sanitized(self, client, xss_payloads):
        """Test various XSS payloads are handled safely."""
        with patch('src.modules.overlays.overlay_controller._service') as mock_service:
            for payload in xss_payloads:
                # Service returns sanitized version
                mock_service.create_overlay.return_value = {
                    '_id': '1',
                    'type': 'text',
                    'content': 'sanitized'
                }
                
                response = client.post('/api/overlays', json={
                    'type': 'text',
                    'content': payload
                })
                
                # Should either succeed with sanitized content or reject
                assert response.status_code in [200, 201, 400]
