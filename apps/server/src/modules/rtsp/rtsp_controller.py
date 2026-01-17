"""RTSP API Controller - REST endpoints for stream management."""

from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from src.utils import error_response, sanitize_error_message

from .rtsp_service import RtspService, StreamConnectionError, StreamValidationError

rtsp_bp = Blueprint('rtsp', __name__, url_prefix='/api/rtsp')


def _get_service() -> RtspService:
    return RtspService(current_app.static_folder)


def _extract_url_from_request(data: Dict[str, Any]) -> str:
    return data.get('url') or data.get('rtsp_url') or ''


def _build_stream_url(stream_path: str) -> str:
    base_url = request.host_url.rstrip('/')
    return f"{base_url}{stream_path}"


@rtsp_bp.route('/connect', methods=['POST'])
def connect():
    data = request.get_json(force=True, silent=True)
    
    if data is None:
        return jsonify(error_response("No data provided", 400)[0]), 400
    
    url = _extract_url_from_request(data)
    if not url:
        return jsonify(error_response("URL is required", 400)[0]), 400
    
    try:
        result = _get_service().connect_stream(url)
        
        if 'streamPath' in result:
            result['streamUrl'] = _build_stream_url(result['streamPath'])
        
        return jsonify(result)
    
    except StreamValidationError as e:
        return jsonify(error_response(str(e), 400)[0]), 400
    except StreamConnectionError as e:
        sanitized_msg = sanitize_error_message(e, "Failed to connect to stream")
        return jsonify(error_response(sanitized_msg, 500)[0]), 500
    except Exception as e:
        sanitized_msg = sanitize_error_message(e, "An unexpected error occurred")
        return jsonify(error_response(sanitized_msg, 500)[0]), 500


@rtsp_bp.route('/disconnect', methods=['POST'])
def disconnect():
    result = _get_service().disconnect_stream()
    return jsonify(result)


@rtsp_bp.route('/status', methods=['GET'])
def status():
    result = _get_service().get_status()
    return jsonify(result)
