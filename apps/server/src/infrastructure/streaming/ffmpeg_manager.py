"""
FFmpeg Stream Manager - Converts RTSP streams to HLS format for browser playback.

Usage:
    FFmpegManager.start_stream("rtsp://example.com/stream", "/path/to/output.m3u8")
    FFmpegManager.stop_stream()
    status = FFmpegManager.get_status()  # Returns "live" or "idle"
"""

import contextlib
import logging
import os
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StreamConfig:
    """Immutable configuration for HLS stream encoding."""
    

    BUFFER_SIZE: int = 4194304
    MAX_DELAY: int = 1000000
    REORDER_QUEUE_SIZE: int = 4000
    TIMEOUT: int = 15000000
    STIMEOUT: int = 15000000
    ANALYZE_DURATION: int = 3000000
    PROBE_SIZE: int = 5000000
    

    VIDEO_BITRATE: str = "1500k"
    VIDEO_MAXRATE: str = "2000k"
    VIDEO_BUFSIZE: str = "4000k"

    KEYFRAME_INTERVAL: int = 30
    
    AUDIO_BITRATE: str = "128k"
    AUDIO_SAMPLE_RATE: int = 44100
    AUDIO_CHANNELS: int = 2
    

    HLS_SEGMENT_DURATION: int = 4
    HLS_LIST_SIZE: int = 6
    
    STARTUP_WAIT: float = 2.0
    PLAYLIST_TIMEOUT: float = 45.0
    POLL_INTERVAL: float = 0.5
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 5


class StreamCommandBuilder(ABC):
    """Abstract base for building stream conversion commands."""
    
    @abstractmethod
    def build(self, input_url: str, output_path: str) -> List[str]:
        pass


class HLSCommandBuilder(StreamCommandBuilder):
    """Builds FFmpeg command for RTSP to HLS conversion with browser-compatible H.264 output."""
    
    def __init__(self, config: Optional[StreamConfig] = None):
        self._config = config or StreamConfig()
    
    def build(self, input_url: str, output_path: str) -> List[str]:
        output_dir = os.path.dirname(output_path)
        segment_pattern = os.path.join(output_dir, 'segment_%03d.ts')
        
        return [
        'ffmpeg', '-y',
        '-loglevel', 'error',
        '-err_detect', 'ignore_err',

        '-fflags', '+genpts+discardcorrupt+nobuffer',

        '-flags', '+low_delay',
        '-flags2', '+fast',
        '-rtsp_transport', 'tcp',
        '-rtsp_flags', 'prefer_tcp',  
        '-timeout', str(self._config.TIMEOUT),
        '-buffer_size', str(self._config.BUFFER_SIZE),
        '-max_delay', str(self._config.MAX_DELAY),
        '-reorder_queue_size', str(self._config.REORDER_QUEUE_SIZE),
        '-analyzeduration', str(self._config.ANALYZE_DURATION),
        '-probesize', str(self._config.PROBE_SIZE),
        '-i', input_url,

        '-map', '0:v:0',
        '-map', '0:a:0?',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-tune', 'zerolatency',
        '-profile:v', 'main',
        '-level', '4.0',
        '-b:v', self._config.VIDEO_BITRATE,
        '-maxrate', self._config.VIDEO_MAXRATE,
        '-bufsize', self._config.VIDEO_BUFSIZE,
        '-g', str(self._config.KEYFRAME_INTERVAL),
        '-keyint_min', str(self._config.KEYFRAME_INTERVAL),
        '-sc_threshold', '0',
        '-pix_fmt', 'yuv420p',
        '-avoid_negative_ts', 'make_zero',
        '-vsync', 'cfr',
        '-c:a', 'aac',
        '-b:a', self._config.AUDIO_BITRATE,
        '-ar', str(self._config.AUDIO_SAMPLE_RATE),
        '-ac', str(self._config.AUDIO_CHANNELS),
        '-f', 'hls',
        '-hls_time', str(self._config.HLS_SEGMENT_DURATION),
        '-hls_list_size', str(self._config.HLS_LIST_SIZE),
        '-hls_flags', 'delete_segments+omit_endlist',
        '-hls_segment_type', 'mpegts',
        '-hls_segment_filename', segment_pattern,
        '-start_number', '1',
        output_path
    ]


class OutputDirectoryManager:
    """Handles HLS output directory creation and cleanup."""
    
    @staticmethod
    def prepare(output_path: str) -> bool:
        output_dir = os.path.dirname(output_path)
        
        if not OutputDirectoryManager._ensure_directory_exists(output_dir):
            return False
        
        OutputDirectoryManager._clean_old_segments(output_dir)
        return True
    
    @staticmethod
    def _ensure_directory_exists(directory: str) -> bool:
        if os.path.exists(directory):
            return True
        
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created HLS directory: {directory}")
            return True
        except OSError as e:
            logger.error(f"Failed to create HLS directory {directory}: {e}")
            return False
    
    @staticmethod
    def _clean_old_segments(directory: str) -> None:
        for filename in os.listdir(directory):
            if filename.endswith((".ts", ".m3u8")):
                with contextlib.suppress(OSError):
                    os.remove(os.path.join(directory, filename))


class FFmpegProcessHandler:
    """Manages FFmpeg subprocess lifecycle and stderr monitoring."""
    
    def __init__(self, config: Optional[StreamConfig] = None):
        self._config = config or StreamConfig()
        self._process: Optional[subprocess.Popen] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._last_error: Optional[str] = None
    
    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None
    
    @property
    def last_error(self) -> Optional[str]:
        return self._last_error
    
    def start(self, command: List[str]) -> bool:
        self._last_error = None
        
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=creation_flags
            )
            self._start_stderr_consumer()
            return True
        except Exception as e:
            logger.error(f"Failed to start FFmpeg: {e}")
            return False
    
    def stop(self) -> None:
        if not self._process:
            return
        
        logger.info("Stopping FFmpeg process...")
        
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=self._config.GRACEFUL_SHUTDOWN_TIMEOUT)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        
        self._process = None
        self._stderr_thread = None
        self._last_error = None
    
    def _start_stderr_consumer(self) -> None:
        self._stderr_thread = threading.Thread(
            target=self._consume_stderr,
            daemon=True
        )
        self._stderr_thread.start()
    
    def _consume_stderr(self) -> None:
        try:
            for line in iter(self._process.stderr.readline, b''):
                if not line:
                    continue
                
                decoded = line.decode('utf-8', errors='replace').strip()
                if not decoded:
                    continue
                
                self._log_stderr_line(decoded)
        except Exception as e:
            logger.error(f"Error reading FFmpeg stderr: {e}")
    
    def _log_stderr_line(self, line: str) -> None:
        line_lower = line.lower()
        
        if 'error' in line_lower or 'failed' in line_lower:
            logger.error(f"FFmpeg: {line}")
            self._last_error = line
        elif 'warning' in line_lower:
            logger.warning(f"FFmpeg: {line}")
        else:
            logger.debug(f"FFmpeg: {line}")


class PlaylistWaiter:
    """Waits for HLS playlist file to be created and populated."""
    
    def __init__(self, config: Optional[StreamConfig] = None):
        self._config = config or StreamConfig()
    
    def wait_for_playlist(
        self,
        output_path: str,
        process_handler: FFmpegProcessHandler
    ) -> bool:
        waited = 0.0
        
        logger.info("Waiting for HLS playlist creation...")
        
        while waited < self._config.PLAYLIST_TIMEOUT:
            if self._playlist_is_ready(output_path):
                logger.info(f"HLS playlist created after {waited:.1f}s")
                return True
            
            if not process_handler.is_running:
                logger.error(f"FFmpeg exited unexpectedly. Code: {process_handler._process.returncode if process_handler._process else 'N/A'}")
                return False
            
            if waited > 0 and waited % 5 == 0:
                logger.info(f"Still waiting for HLS playlist... ({waited:.0f}s)")
            
            time.sleep(self._config.POLL_INTERVAL)
            waited += self._config.POLL_INTERVAL
        
        logger.error(f"HLS playlist not created after {self._config.PLAYLIST_TIMEOUT}s")
        return False
    
    def _playlist_is_ready(self, path: str) -> bool:
        return os.path.exists(path) and os.path.getsize(path) > 0


class FFmpegManager:
    """
    Singleton manager for RTSP to HLS stream conversion.
    
    Provides class-level methods to start/stop streams and query status.
    Only one stream can be active at a time.
    Thread-safe using a class-level lock.
    """
    
    _process_handler: FFmpegProcessHandler = FFmpegProcessHandler()
    _command_builder: StreamCommandBuilder = HLSCommandBuilder()
    _playlist_waiter: PlaylistWaiter = PlaylistWaiter()
    _config: StreamConfig = StreamConfig()
    _current_url: Optional[str] = None
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def start_stream(cls, rtsp_url: str, output_path: str) -> bool:
        with cls._lock:
            if cls._process_handler.is_running:
                cls._stop_stream_unsafe()
            
            if not OutputDirectoryManager.prepare(output_path):
                return False
            
            command = cls._command_builder.build(rtsp_url, output_path)
            logger.info(f"Starting stream: {rtsp_url}")
            
            if not cls._process_handler.start(command):
                return False
            
            time.sleep(cls._config.STARTUP_WAIT)
            
            if not cls._process_handler.is_running:
                logger.error("FFmpeg exited immediately after startup")
                return False
            
            if not cls._playlist_waiter.wait_for_playlist(output_path, cls._process_handler):
                cls._stop_stream_unsafe()
                return False
            
            cls._current_url = rtsp_url
            logger.info("Stream started successfully")
            return True
    
    @classmethod
    def stop_stream(cls) -> None:
        with cls._lock:
            cls._stop_stream_unsafe()
    
    @classmethod
    def _stop_stream_unsafe(cls) -> None:
        """Internal method to stop stream without acquiring lock."""
        cls._process_handler.stop()
        cls._current_url = None
    
    @classmethod
    def get_status(cls) -> str:
        with cls._lock:
            return "live" if cls._process_handler.is_running else "idle"
    
    @classmethod
    def get_current_url(cls) -> Optional[str]:
        return cls._current_url
    
    @classmethod
    def get_last_error(cls) -> Optional[str]:
        return cls._process_handler.last_error
