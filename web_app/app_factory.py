import os
import sys
import warnings
from flask import Flask, jsonify

warnings.filterwarnings("ignore", category=UserWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from web_app.config import Config
from web_app.blueprints.views import views_bp
from web_app.blueprints.auth import auth_bp
from web_app.blueprints.models import models_bp
from web_app.blueprints.chat import chat_bp
from web_app.blueprints.telemetry import telemetry_bp

def create_app(config_class=Config):
    """
    Application Factory Pattern.
    Modularizes web application routes into isolated Blueprints to eliminate Single Points of Failure (SPOF).
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'templates'),
        static_folder=os.path.join(BASE_DIR, 'static')
    )
    app.config.from_object(config_class)

    # Register Modular Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(telemetry_bp)

    # Global Resilience Error Handlers (Zero SPOF)
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"status": "error", "message": "Resource or endpoint not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        print(f"Global 500 internal server error: {error}")
        return jsonify({"status": "error", "message": "An internal error occurred, but the system recovered safely."}), 500

    return app
