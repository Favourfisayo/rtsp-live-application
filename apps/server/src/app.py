"""
RTSP Overlay Backend Application

Flask application that provides:
- RTSP stream conversion to HLS for browser playback
- Overlay management API (CRUD operations)
- Static file serving for HLS segments for browser compatibility

Run with: python -m src.app
"""

import logging
import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from my_app_config import MONGODB_SETTINGS
from my_app_db import init_db
from src.modules.overlays.overlay_controller import overlay_bp
from src.modules.rtsp.rtsp_controller import rtsp_bp

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_static_folder() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'static')


def create_app() -> Flask:
    static_folder = get_static_folder()
    
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    
   
    app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    

    limiter.init_app(app)
    
    init_db(app)
    
    app.register_blueprint(rtsp_bp)
    app.register_blueprint(overlay_bp)
    
    _register_cors_handler(app)
    _register_health_route(app)
    
    return app


def _register_cors_handler(app: Flask) -> None:
    allowed_origin = os.getenv('CORS_ORIGIN')
    
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = allowed_origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response


def _register_health_route(app: Flask) -> None:
    @app.route("/")
    def health_check():
        return "<p>RTSP Overlay Backend Running</p>"


configure_logging()
app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    app.run(host=host, port=port, debug=debug_mode)
