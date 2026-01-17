"""RTSP Stream Service - Handles stream connection lifecycle and status."""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.infrastructure.streaming.ffmpeg_manager import FFmpegManager
from src.validators.rtsp_validators import RtspUrlValidator

logger = logging.getLogger(__name__)


class StreamValidationError(ValueError):
    pass


class StreamConnectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class StreamResponse:
    status: str
    url: Optional[str] = None
    stream_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"status": self.status}
        if self.url:
            result["url"] = self.url
        if self.stream_path:
            result["streamPath"] = self.stream_path
        return result


class StreamManager(ABC):
    @abstractmethod
    def start(self, url: str, output_path: str) -> bool:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        pass
    
    @abstractmethod
    def get_current_url(self) -> Optional[str]:
        pass
    
    @abstractmethod
    def get_last_error(self) -> Optional[str]:
        pass


class FFmpegStreamManager(StreamManager):
    def start(self, url: str, output_path: str) -> bool:
        return FFmpegManager.start_stream(url, output_path)
    
    def stop(self) -> None:
        FFmpegManager.stop_stream()
    
    def get_status(self) -> str:
        return FFmpegManager.get_status()
    
    def get_current_url(self) -> Optional[str]:
        return FFmpegManager.get_current_url()
    
    def get_last_error(self) -> Optional[str]:
        return FFmpegManager.get_last_error()


class RtspService:
    HLS_OUTPUT_PATH = "hls/stream.m3u8"
    STREAM_PATH = "/static/hls/stream.m3u8"
    
    def __init__(
        self,
        static_folder: str,
        stream_manager: Optional[StreamManager] = None,
        validator: Optional[RtspUrlValidator] = None
    ):
        self._output_path = os.path.join(static_folder, self.HLS_OUTPUT_PATH)
        self._stream_manager = stream_manager or FFmpegStreamManager()
        self._validator = validator or RtspUrlValidator()
    
    def connect_stream(self, rtsp_url: str) -> Dict[str, Any]:
        self._validate_url(rtsp_url)
        self._start_stream(rtsp_url)
        
        return StreamResponse(
            status="live",
            url=rtsp_url,
            stream_path=self.STREAM_PATH
        ).to_dict()
    
    def disconnect_stream(self) -> Dict[str, Any]:
        self._stream_manager.stop()
        return StreamResponse(status="disconnected").to_dict()
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self._stream_manager.get_status(),
            "url": self._stream_manager.get_current_url()
        }
    
    def _validate_url(self, url: str) -> None:
        if not self._validator.is_valid(url):
            raise StreamValidationError("Invalid RTSP URL format")
    
    def _start_stream(self, url: str) -> None:
        logger.info(f"Starting stream: {url}")
        
        if not self._stream_manager.start(url, self._output_path):
            error = self._stream_manager.get_last_error()
            raise StreamConnectionError(
                f"Failed to start stream: {error}" if error
                else "Failed to start stream - verify RTSP URL is accessible"
            )
