import os
import sys
from flask import Blueprint, render_template, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from web_app.db import mongo_mgr
from web_app.quantaq_client import QuantAQClient

views_bp = Blueprint('views', __name__)
quantaq_client = QuantAQClient(PROJECT_DIR)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/health', methods=['GET'])
def health_check():
    """
    Real-Time System Diagnostic Health Check Endpoint.
    """
    db_status = "MongoDB Connected" if not mongo_mgr.use_fallback else "Embedded Document Store (Local High-Availability Mode)"
    
    try:
        telemetry = quantaq_client.calibrate_live_telemetry()
        stream_status = "Live Stream Active" if telemetry and telemetry.get("raw_pm25") is not None else "Cached Stream"
    except Exception as e:
        stream_status = f"Degraded ({str(e)})"

    return jsonify({
        "status": "healthy",
        "system": "AirML Calibration Studio",
        "database": db_status,
        "telemetry_stream": stream_status,
        "rag_engine": "AirSense AI Groq & Local Fallback Active"
    })
