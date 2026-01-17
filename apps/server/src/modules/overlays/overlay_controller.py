"""Overlay API Controller - REST endpoints for overlay management."""


from flask import Blueprint, jsonify, request

from src.utils import error_response, sanitize_error_message, validate_id_parameter
from src.validators.overlay_validators import (
    validate_overlay_data,
    validate_overlay_update_data,
)

from .overlay_service import ImageDownloadError, OverlayService

overlay_bp = Blueprint('overlays', __name__, url_prefix='/api/overlays')
_service = OverlayService()


@overlay_bp.route('', methods=['GET'])
def get_overlays():
    return jsonify(_service.get_all_overlays())


@overlay_bp.route('', methods=['POST'])
def create_overlay():
    data = request.get_json(force=True, silent=True)
    
    if data is None:
        return jsonify(error_response("No data provided", 400)[0]), 400
    
    is_valid, error_message = validate_overlay_data(data)
    if not is_valid:
        return jsonify(error_response(f"Validation error: {error_message}", 400)[0]), 400
    
    try:
        result = _service.create_overlay(data)
        return jsonify(result), 201
    except ImageDownloadError as e:
        return jsonify(error_response(str(e), 400)[0]), 400
    except Exception as e:
        sanitized_msg = sanitize_error_message(e, "Failed to create overlay")
        return jsonify(error_response(sanitized_msg, 500)[0]), 500


@overlay_bp.route('/<id>', methods=['GET'])
def get_overlay(id: str):
    if not validate_id_parameter(id):
        return jsonify(error_response("Invalid ID parameter", 400)[0]), 400
    
    result = _service.get_overlay(id)
    
    if not result:
        return jsonify(error_response("Overlay not found", 404)[0]), 404
    
    return jsonify(result)


@overlay_bp.route('/<id>', methods=['PUT', 'PATCH'])
def update_overlay(id: str):
    if not validate_id_parameter(id):
        return jsonify(error_response("Invalid ID parameter", 400)[0]), 400
    
    data = request.get_json(force=True, silent=True)
    
    if data is None:
        return jsonify(error_response("No data provided", 400)[0]), 400
    
    is_valid, error_message = validate_overlay_update_data(data)
    if not is_valid:
        return jsonify(error_response(f"Validation error: {error_message}", 400)[0]), 400
    
    try:
        result = _service.update_overlay(id, data)
        
        if not result:
            return jsonify(error_response("Overlay not found", 404)[0]), 404
        
        return jsonify(result)
    except ImageDownloadError as e:
        return jsonify(error_response(str(e), 400)[0]), 400
    except Exception as e:
        sanitized_msg = sanitize_error_message(e, "Failed to update overlay")
        return jsonify(error_response(sanitized_msg, 500)[0]), 500


@overlay_bp.route('/<id>', methods=['DELETE'])
def delete_overlay(id: str):
    if not validate_id_parameter(id):
        return jsonify(error_response("Invalid ID parameter", 400)[0]), 400
    
    if not _service.delete_overlay(id):
        return jsonify(error_response("Overlay not found", 404)[0]), 404
    
    return jsonify({"message": "Overlay deleted"})
