"""Unit tests for RTSP URL validators."""

from src.validators.rtsp_validators import validate_rtsp_url


class TestRtspUrlValidator:
    """Tests for RtspUrlValidator class."""
    
    def test_valid_basic_rtsp_url(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://192.168.1.100/stream') is True
    
    def test_valid_rtsp_url_with_port(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://192.168.1.100:554/stream') is True
    
    def test_valid_rtsp_url_with_credentials(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://user:pass@192.168.1.100/stream') is True
    
    def test_valid_rtsp_url_with_hostname(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://camera.example.com/live') is True
    
    def test_valid_rtsp_url_localhost(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://localhost/test') is True
    
    def test_valid_rtsp_url_with_path(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/live/stream1/main') is True
    
    def test_valid_rtsp_url_with_query_params(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/stream?token=abc123') is True
    
    def test_multiple_valid_urls(self, rtsp_validator, valid_rtsp_urls):
        for url in valid_rtsp_urls:
            assert rtsp_validator.is_valid(url) is True, f"URL should be valid: {url}"
    
    def test_invalid_http_url(self, rtsp_validator):
        assert rtsp_validator.is_valid('http://example.com/stream') is False
    
    def test_invalid_https_url(self, rtsp_validator):
        assert rtsp_validator.is_valid('https://example.com/stream') is False
    
    def test_invalid_ftp_url(self, rtsp_validator):
        assert rtsp_validator.is_valid('ftp://example.com/file') is False
    
    def test_invalid_file_url(self, rtsp_validator):
        assert rtsp_validator.is_valid('file:///etc/passwd') is False
    
    def test_invalid_empty_string(self, rtsp_validator):
        assert rtsp_validator.is_valid('') is False
    
    def test_invalid_whitespace_only(self, rtsp_validator):
        assert rtsp_validator.is_valid('   ') is False
    
    def test_invalid_rtsp_scheme_only(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://') is False
    
    def test_invalid_no_scheme(self, rtsp_validator):
        assert rtsp_validator.is_valid('example.com/stream') is False
    
    def test_invalid_plain_text(self, rtsp_validator):
        assert rtsp_validator.is_valid('not-a-url') is False
    
    def test_injection_semicolon(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/stream;rm -rf /') is False
    
    def test_injection_pipe(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/stream|cat /etc/passwd') is False
    
    def test_injection_backtick(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/`whoami`') is False
    
    def test_injection_dollar_paren(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/$(id)') is False
    
    def test_injection_multiple_attacks(self, rtsp_validator):
        assert rtsp_validator.is_valid('rtsp://example.com/;|`$()') is False
    
    def test_multiple_invalid_urls(self, rtsp_validator, invalid_rtsp_urls):
        for url in invalid_rtsp_urls:
            assert rtsp_validator.is_valid(url) is False, f"URL should be invalid: {url}"


class TestValidateRtspUrlFunction:
    """Tests for validate_rtsp_url convenience function."""
    
    def test_valid_url(self):
        assert validate_rtsp_url('rtsp://camera/stream') is True
    
    def test_invalid_url(self):
        assert validate_rtsp_url('http://youtube.com') is False
    
    def test_injection_blocked(self):
        assert validate_rtsp_url('rtsp://x;rm -rf /') is False
