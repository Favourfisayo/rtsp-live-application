"""End-to-end tests for complete stream and overlay workflows.

Tests cover:
- Complete flow: start stream → create overlay → update → stop stream
- Multiple overlay management during stream
- State consistency throughout workflow
"""

from unittest.mock import MagicMock, patch


class TestStreamOverlayE2EFlow:
    """E2E tests for complete stream + overlay workflows."""
    
    def test_complete_stream_overlay_flow(self, client):
        """
        Test complete workflow:
        1. Start RTSP stream
        2. Create overlay
        3. Update overlay
        4. Get overlays
        5. Stop stream
        """

        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_rtsp_service, \
             patch('src.modules.overlays.overlay_controller._service') as mock_overlay_service:
            

            rtsp_service = MagicMock()
            rtsp_service.connect_stream.return_value = {
                'status': 'live',
                'url': 'rtsp://camera/stream',
                'streamPath': '/static/hls/stream.m3u8'
            }
            rtsp_service.disconnect_stream.return_value = {
                'status': 'disconnected'
            }
            rtsp_service.get_status.return_value = {
                'status': 'live',
                'url': 'rtsp://camera/stream'
            }
            mock_rtsp_service.return_value = rtsp_service
            

            overlays = {}
            overlay_counter = [0]
            
            def create_overlay(data):
                overlay_counter[0] += 1
                overlay_id = str(overlay_counter[0])
                overlay = {
                    '_id': overlay_id,
                    'type': data.get('type'),
                    'content': data.get('content'),
                    'x': data.get('x', 0),
                    'y': data.get('y', 0),
                    'visible': True
                }
                overlays[overlay_id] = overlay
                return overlay
            
            def get_all_overlays():
                return list(overlays.values())
            
            def update_overlay(overlay_id, data):
                if overlay_id in overlays:
                    overlays[overlay_id].update(data)
                    return overlays[overlay_id]
                return None
            
            mock_overlay_service.create_overlay.side_effect = create_overlay
            mock_overlay_service.get_all_overlays.side_effect = get_all_overlays
            mock_overlay_service.update_overlay.side_effect = update_overlay
            
            # Step 1: Start stream
            response = client.post('/api/rtsp/connect', json={
                'url': 'rtsp://camera/stream'
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'live'
            
            # Step 2: Create overlay
            response = client.post('/api/overlays', json={
                'type': 'text',
                'content': 'LIVE',
                'x': 10,
                'y': 10
            })
            assert response.status_code == 201
            overlay_id = response.get_json()['_id']
            
            # Step 3: Update overlay
            response = client.put(f'/api/overlays/{overlay_id}', json={
                'content': 'LIVE - Updated'
            })
            assert response.status_code == 200
            assert response.get_json()['content'] == 'LIVE - Updated'
            
            # Step 4: Get all overlays
            response = client.get('/api/overlays')
            assert response.status_code == 200
            overlays_list = response.get_json()
            assert len(overlays_list) == 1
            
            # Step 5: Stop stream
            response = client.post('/api/rtsp/disconnect')
            assert response.status_code == 200
            assert response.get_json()['status'] == 'disconnected'
    
    def test_multiple_overlays_during_stream(self, client):
        """Test creating and managing multiple overlays during a stream."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_rtsp_service, \
             patch('src.modules.overlays.overlay_controller._service') as mock_overlay_service:
            

            rtsp_service = MagicMock()
            rtsp_service.connect_stream.return_value = {
                'status': 'live',
                'url': 'rtsp://stream',
                'streamPath': '/static/hls/stream.m3u8'
            }
            mock_rtsp_service.return_value = rtsp_service
            

            overlay_storage = []
            counter = [0]
            
            def create(data):
                counter[0] += 1
                overlay = {'_id': str(counter[0]), **data}
                overlay_storage.append(overlay)
                return overlay
            
            def delete(overlay_id):
                for i, o in enumerate(overlay_storage):
                    if o['_id'] == overlay_id:
                        overlay_storage.pop(i)
                        return True
                return False
            
            mock_overlay_service.create_overlay.side_effect = create
            mock_overlay_service.get_all_overlays.side_effect = lambda: overlay_storage.copy()
            mock_overlay_service.delete_overlay.side_effect = delete
            

            client.post('/api/rtsp/connect', json={'url': 'rtsp://stream'})
            

            client.post('/api/overlays', json={
                'type': 'text',
                'content': 'Watermark'
            })
            client.post('/api/overlays', json={
                'type': 'image',
                'content': 'https://example.com/logo.png'
            })
            client.post('/api/overlays', json={
                'type': 'text',
                'content': 'Timestamp'
            })
            
            response = client.get('/api/overlays')
            assert len(response.get_json()) == 3
            
            # Delete one overlay
            client.delete('/api/overlays/2')
            

            response = client.get('/api/overlays')
            assert len(response.get_json()) == 2
    
    def test_overlay_persistence_across_stream_restart(self, client):
        """Test that overlays persist when stream is restarted."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_rtsp_service, \
             patch('src.modules.overlays.overlay_controller._service') as mock_overlay_service:
            
            # Persistent overlay storage (simulating database)
            persistent_overlays = []
            
            rtsp_service = MagicMock()
            rtsp_service.connect_stream.return_value = {
                'status': 'live',
                'streamPath': '/static/hls/stream.m3u8'
            }
            rtsp_service.disconnect_stream.return_value = {'status': 'disconnected'}
            mock_rtsp_service.return_value = rtsp_service
            
            def create(data):
                overlay = {'_id': str(len(persistent_overlays) + 1), **data}
                persistent_overlays.append(overlay)
                return overlay
            
            mock_overlay_service.create_overlay.side_effect = create
            mock_overlay_service.get_all_overlays.side_effect = lambda: persistent_overlays.copy()
            
            # First stream session
            client.post('/api/rtsp/connect', json={'url': 'rtsp://stream'})
            client.post('/api/overlays', json={'type': 'text', 'content': 'Persistent'})
            client.post('/api/rtsp/disconnect')
            
            # Second stream session
            client.post('/api/rtsp/connect', json={'url': 'rtsp://stream'})
            
            # Overlays should still be there
            response = client.get('/api/overlays')
            assert len(response.get_json()) == 1
            assert response.get_json()[0]['content'] == 'Persistent'


class TestErrorRecoveryE2E:
    """E2E tests for error recovery scenarios."""
    
    def test_overlay_operations_after_stream_failure(self, client):
        """Test that overlay operations work after stream connection failure."""
        from src.modules.rtsp.rtsp_service import StreamConnectionError
        
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_rtsp_service, \
             patch('src.modules.overlays.overlay_controller._service') as mock_overlay_service:
            
            rtsp_service = MagicMock()
            rtsp_service.connect_stream.side_effect = StreamConnectionError('Connection refused')
            mock_rtsp_service.return_value = rtsp_service
            
            mock_overlay_service.create_overlay.return_value = {
                '_id': '1',
                'type': 'text',
                'content': 'Test'
            }
            mock_overlay_service.get_all_overlays.return_value = []
            
            # Stream fails
            response = client.post('/api/rtsp/connect', json={'url': 'rtsp://bad-stream'})
            assert response.status_code == 500
            
            # Overlay operations should still work
            response = client.post('/api/overlays', json={
                'type': 'text',
                'content': 'Test'
            })
            assert response.status_code == 201
            
            response = client.get('/api/overlays')
            assert response.status_code == 200
    
    def test_stream_operations_independent_of_overlays(self, client):
        """Test that stream operations work regardless of overlay state."""
        with patch('src.modules.rtsp.rtsp_controller._get_service') as mock_rtsp_service, \
             patch('src.modules.overlays.overlay_controller._service') as mock_overlay_service:
            
            rtsp_service = MagicMock()
            rtsp_service.connect_stream.return_value = {
                'status': 'live',
                'streamPath': '/static/hls/stream.m3u8'
            }
            rtsp_service.get_status.return_value = {'status': 'live'}
            mock_rtsp_service.return_value = rtsp_service
            
            # Overlay service throws error
            mock_overlay_service.get_all_overlays.side_effect = Exception('DB error')
            
            # Stream operations should still work
            response = client.post('/api/rtsp/connect', json={'url': 'rtsp://stream'})
            assert response.status_code == 200
            
            response = client.get('/api/rtsp/status')
            assert response.status_code == 200


class TestHealthCheckE2E:
    """E2E tests for application health."""
    
    def test_health_endpoint_accessible(self, client):
        """Test that health endpoint is accessible."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Running' in response.data
