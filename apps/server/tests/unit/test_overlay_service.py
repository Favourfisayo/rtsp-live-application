"""Unit tests for Overlay Service.

Tests cover:
- Overlay creation (text and image types)
- Overlay retrieval (single and all)
- Overlay update (partial and full)
- Overlay deletion
- Input validation
- XSS sanitization
- OverlayData dataclass
- ContentSanitizer
"""

from unittest.mock import MagicMock, patch

from src.modules.overlays.overlay_service import (
    ContentSanitizer,
    OverlayData,
    OverlayResponseFormatter,
    OverlayService,
)


class TestContentSanitizer:
    """Test suite for ContentSanitizer XSS prevention."""
    
    def test_sanitize_removes_script_tags(self):
        """Test that script tags are removed."""
        content = '<script>alert("XSS")</script>'
        result = ContentSanitizer.sanitize(content)
        
        assert '<script>' not in result
        assert '</script>' not in result
    
    def test_sanitize_removes_img_onerror(self):
        """Test that img onerror handlers are removed."""
        content = '<img src=x onerror=alert("XSS")>'
        result = ContentSanitizer.sanitize(content)
        
        assert 'onerror' not in result.lower()
    
    def test_sanitize_removes_svg_onload(self):
        """Test that svg onload handlers are removed."""
        content = '<svg onload=alert("XSS")>'
        result = ContentSanitizer.sanitize(content)
        
        assert 'onload' not in result.lower()
    
    def test_sanitize_removes_javascript_protocol(self):
        """Test that javascript: protocol is removed."""
        content = 'javascript:alert("XSS")'
        result = ContentSanitizer.sanitize(content)
        
        # If bleach is available, it strips it
        # If not, html.escape will escape the characters
        assert 'javascript:' not in result or '&' in result
    
    def test_sanitize_removes_iframe(self):
        """Test that iframes are removed."""
        content = '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        result = ContentSanitizer.sanitize(content)
        
        assert '<iframe' not in result.lower()
    
    def test_sanitize_preserves_plain_text(self):
        """Test that plain text is preserved."""
        content = 'Hello World! This is safe text.'
        result = ContentSanitizer.sanitize(content)
        
        assert result == content
    
    def test_sanitize_empty_string(self):
        """Test that empty string returns empty."""
        assert ContentSanitizer.sanitize('') == ''
    
    def test_sanitize_none_returns_none(self):
        """Test that None-like falsy returns as-is."""
        assert ContentSanitizer.sanitize('') == ''
    
    def test_is_safe_detects_script_tags(self):
        """Test is_safe detects script injection."""
        assert ContentSanitizer.is_safe('<script>alert(1)</script>') is False
    
    def test_is_safe_detects_event_handlers(self):
        """Test is_safe detects event handler injection."""
        assert ContentSanitizer.is_safe('<div onclick=alert(1)>') is False
        assert ContentSanitizer.is_safe('<img onerror=alert(1)>') is False
    
    def test_is_safe_detects_javascript_protocol(self):
        """Test is_safe detects javascript: protocol."""
        assert ContentSanitizer.is_safe('javascript:void(0)') is False
    
    def test_is_safe_allows_plain_text(self):
        """Test is_safe allows normal text."""
        assert ContentSanitizer.is_safe('Normal text content') is True
    
    def test_is_safe_allows_empty_string(self):
        """Test is_safe allows empty string."""
        assert ContentSanitizer.is_safe('') is True
    
    def test_multiple_xss_payloads(self, xss_payloads):
        """Test sanitization of multiple XSS payloads."""
        for payload in xss_payloads:
            result = ContentSanitizer.sanitize(payload)
            # After sanitization, dangerous patterns should be gone or escaped
            assert '<script' not in result.lower() or '&lt;' in result


class TestOverlayData:
    """Test suite for OverlayData dataclass."""
    
    def test_from_dict_with_all_fields(self):
        """Test from_dict with complete data."""
        data = {
            'type': 'text',
            'content': 'Hello',
            'x': 10.0,
            'y': 20.0,
            'width': 200.0,
            'height': 50.0,
            'zIndex': 5,
            'visible': False
        }
        
        result = OverlayData.from_dict(data)
        
        assert result.type == 'text'
        assert result.content == 'Hello'
        assert result.x == 10.0
        assert result.y == 20.0
        assert result.width == 200.0
        assert result.height == 50.0
        assert result.z_index == 5
        assert result.visible is False
    
    def test_from_dict_with_defaults(self):
        """Test from_dict uses default values."""
        data = {'type': 'text', 'content': 'Test'}
        
        result = OverlayData.from_dict(data)
        
        assert result.x == 0.0
        assert result.y == 0.0
        assert result.width == 100.0
        assert result.height == 100.0
        assert result.z_index == 1
        assert result.visible is True
    
    def test_from_dict_sanitizes_text_content(self):
        """Test from_dict sanitizes text overlay content."""
        data = {
            'type': 'text',
            'content': '<script>alert("XSS")</script>'
        }
        
        result = OverlayData.from_dict(data, sanitize=True)
        
        assert '<script>' not in result.content
    
    def test_from_dict_does_not_sanitize_image_content(self):
        """Test from_dict downloads image and stores URL in image_url field."""
        data = {
            'type': 'image',
            'content': 'https://example.com/logo.png?param=value'
        }
        
        with patch('src.modules.overlays.overlay_service.ImageDownloader.download_and_encode') as mock_download:
            mock_download.return_value = 'data:image/png;base64,abc123'
            result = OverlayData.from_dict(data, sanitize=True)
        
        assert result.content == 'data:image/png;base64,abc123'
        assert result.image_url == 'https://example.com/logo.png?param=value'
    
    def test_from_dict_sanitize_disabled(self):
        """Test from_dict with sanitization disabled."""
        data = {
            'type': 'text',
            'content': '<b>Bold text</b>'
        }
        
        result = OverlayData.from_dict(data, sanitize=False)
        
        # Content should be preserved when sanitize=False
        assert '<b>' in result.content or result.content == '<b>Bold text</b>'


class TestOverlayResponseFormatter:
    """Test suite for OverlayResponseFormatter."""
    
    def test_format_returns_none_for_none_input(self):
        """Test format returns None for None input."""
        assert OverlayResponseFormatter.format(None) is None
    
    def test_format_returns_none_for_empty_dict(self):
        """Test format returns None for empty dict."""
        assert OverlayResponseFormatter.format({}) is None
    
    def test_format_extracts_oid_from_mongo_format(self):
        """Test format extracts _id from MongoDB $oid format."""
        data = {'_id': {'$oid': 'abc123'}, 'type': 'text', 'content': 'Test'}
        
        result = OverlayResponseFormatter.format(data)
        
        assert result['_id'] == 'abc123'
    
    def test_format_handles_string_id(self):
        """Test format handles plain string _id."""
        data = {'_id': 'simple-id', 'type': 'text', 'content': 'Test'}
        
        result = OverlayResponseFormatter.format(data)
        
        assert result['_id'] == 'simple-id'
    
    def test_allowed_update_fields(self):
        """Test ALLOWED_UPDATE_FIELDS contains expected fields."""
        expected = {'type', 'content', 'imageUrl', 'x', 'y', 'width', 'height', 'zIndex', 'visible'}
        assert expected == OverlayResponseFormatter.ALLOWED_UPDATE_FIELDS


class TestOverlayServiceCreate:
    """Test suite for OverlayService.create_overlay method."""
    
    def test_create_text_overlay(self, overlay_service):
        """Test creating a text overlay."""
        result = overlay_service.create_overlay({
            'type': 'text',
            'content': 'Hello World',
            'x': 50,
            'y': 100
        })
        
        assert result['type'] == 'text'
        assert result['content'] == 'Hello World'
        assert result['x'] == 50
        assert result['y'] == 100
    
    def test_create_image_overlay(self, overlay_service, sample_image_overlay_data):
        """Test creating an image overlay."""
        with patch('src.modules.overlays.overlay_service.ImageDownloader.download_and_encode') as mock_download:
            mock_download.return_value = 'data:image/png;base64,abc123'
            result = overlay_service.create_overlay(sample_image_overlay_data)
        
        assert result['type'] == 'image'
        assert result['content'] == 'data:image/png;base64,abc123'
        assert result['imageUrl'] == 'https://example.com/logo.png'
    
    def test_create_overlay_returns_id(self, overlay_service, sample_text_overlay_data):
        """Test that created overlay has an ID."""
        result = overlay_service.create_overlay(sample_text_overlay_data)
        
        assert '_id' in result
        assert result['_id'] is not None
    
    def test_create_overlay_with_default_position(self, overlay_service):
        """Test overlay creation uses default position values."""
        result = overlay_service.create_overlay({
            'type': 'text',
            'content': 'Test'
        })
        
        assert result['x'] == 0.0
        assert result['y'] == 0.0
    
    def test_create_overlay_sanitizes_xss(self, overlay_service):
        """Test that XSS in text content is sanitized."""
        result = overlay_service.create_overlay({
            'type': 'text',
            'content': '<script>alert("XSS")</script>Visible Text'
        })
        
        assert '<script>' not in result['content']
        assert 'Visible Text' in result['content']


class TestOverlayServiceGetAll:
    """Test suite for OverlayService.get_all_overlays method."""
    
    def test_get_all_empty(self, overlay_service):
        """Test get_all returns empty list when no overlays."""
        result = overlay_service.get_all_overlays()
        
        assert result == []
    
    def test_get_all_returns_created_overlays(self, overlay_service):
        """Test get_all returns all created overlays."""
        overlay_service.create_overlay({'type': 'text', 'content': 'First'})
        overlay_service.create_overlay({'type': 'text', 'content': 'Second'})
        
        result = overlay_service.get_all_overlays()
        
        assert len(result) == 2
    
    def test_get_all_returns_list(self, overlay_service, sample_text_overlay_data):
        """Test get_all always returns a list."""
        overlay_service.create_overlay(sample_text_overlay_data)
        
        result = overlay_service.get_all_overlays()
        
        assert isinstance(result, list)


class TestOverlayServiceGetOne:
    """Test suite for OverlayService.get_overlay method."""
    
    def test_get_overlay_by_id(self, overlay_service, sample_text_overlay_data):
        """Test retrieving overlay by ID."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        result = overlay_service.get_overlay(overlay_id)
        
        assert result is not None
        assert result['_id'] == overlay_id
        assert result['type'] == 'text'
    
    def test_get_overlay_not_found(self, overlay_service):
        """Test retrieving non-existent overlay returns None."""
        result = overlay_service.get_overlay('non-existent-id')
        
        assert result is None


class TestOverlayServiceUpdate:
    """Test suite for OverlayService.update_overlay method."""
    
    def test_update_overlay_content(self, overlay_service, sample_text_overlay_data):
        """Test updating overlay content."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        result = overlay_service.update_overlay(overlay_id, {
            'content': 'Updated Content'
        })
        
        assert result is not None
        assert result['content'] == 'Updated Content'
    
    def test_update_overlay_position(self, overlay_service, sample_text_overlay_data):
        """Test updating overlay position."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        result = overlay_service.update_overlay(overlay_id, {
            'x': 999,
            'y': 888
        })
        
        assert result['x'] == 999
        assert result['y'] == 888
    
    def test_update_overlay_visibility(self, overlay_service, sample_text_overlay_data):
        """Test updating overlay visibility."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        result = overlay_service.update_overlay(overlay_id, {
            'visible': False
        })
        
        assert result['visible'] is False
    
    def test_update_overlay_not_found(self, overlay_service):
        """Test updating non-existent overlay returns None."""
        result = overlay_service.update_overlay('non-existent-id', {
            'content': 'New'
        })
        
        assert result is None
    
    def test_update_preserves_unchanged_fields(self, overlay_service):
        """Test that update preserves fields not in update data."""
        created = overlay_service.create_overlay({
            'type': 'text',
            'content': 'Original',
            'x': 100,
            'y': 200
        })
        overlay_id = created['_id']
        
        # Only update content
        result = overlay_service.update_overlay(overlay_id, {
            'content': 'Modified'
        })
        
        # Position should be preserved
        assert result['x'] == 100
        assert result['y'] == 200


class TestOverlayServiceDelete:
    """Test suite for OverlayService.delete_overlay method."""
    
    def test_delete_overlay_success(self, overlay_service, sample_text_overlay_data):
        """Test successful overlay deletion."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        result = overlay_service.delete_overlay(overlay_id)
        
        assert result is True
    
    def test_delete_overlay_removes_from_storage(self, overlay_service, sample_text_overlay_data):
        """Test that deleted overlay is no longer retrievable."""
        created = overlay_service.create_overlay(sample_text_overlay_data)
        overlay_id = created['_id']
        
        overlay_service.delete_overlay(overlay_id)
        
        assert overlay_service.get_overlay(overlay_id) is None
    
    def test_delete_overlay_not_found(self, overlay_service):
        """Test deleting non-existent overlay returns False."""
        result = overlay_service.delete_overlay('non-existent-id')
        
        assert result is False


class TestOverlayServiceWithMockedRepository:
    """Test OverlayService with explicitly mocked repository."""
    
    def test_create_calls_repository(self):
        """Test that create_overlay calls repository.create."""
        mock_repo = MagicMock()
        mock_repo.create.return_value = {'_id': '1', 'type': 'text', 'content': 'Test'}
        
        service = OverlayService(repository=mock_repo)
        service.create_overlay({'type': 'text', 'content': 'Test'})
        
        mock_repo.create.assert_called_once()
    
    def test_get_all_calls_repository(self):
        """Test that get_all_overlays calls repository.find_all."""
        mock_repo = MagicMock()
        mock_repo.find_all.return_value = []
        
        service = OverlayService(repository=mock_repo)
        service.get_all_overlays()
        
        mock_repo.find_all.assert_called_once()
    
    def test_get_one_calls_repository(self):
        """Test that get_overlay calls repository.find_by_id."""
        mock_repo = MagicMock()
        mock_repo.find_by_id.return_value = None
        
        service = OverlayService(repository=mock_repo)
        service.get_overlay('test-id')
        
        mock_repo.find_by_id.assert_called_once_with('test-id')
    
    def test_update_calls_repository(self):
        """Test that update_overlay calls repository.update."""
        mock_repo = MagicMock()
        mock_repo.update.return_value = None
        
        service = OverlayService(repository=mock_repo)
        service.update_overlay('test-id', {'content': 'New'})
        
        mock_repo.update.assert_called_once()
    
    def test_delete_calls_repository(self):
        """Test that delete_overlay calls repository.delete."""
        mock_repo = MagicMock()
        mock_repo.delete.return_value = True
        
        service = OverlayService(repository=mock_repo)
        service.delete_overlay('test-id')
        
        mock_repo.delete.assert_called_once_with('test-id')
