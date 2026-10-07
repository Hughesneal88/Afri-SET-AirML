import os
import sys
import io
import pandas as pd
from flask import Blueprint, request, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from web_app.db import save_raw_telemetry_batch, get_model_retrain_logs
from web_app.retrain_engine import process_reference_upload_and_retrain

data_ingest_bp = Blueprint('data_ingest', __name__, url_prefix='/api')

@data_ingest_bp.route('/telemetry/ingest', methods=['POST'])
def ingest_telemetry():
    """
    Ingests live raw sensor readings into database for future continuous learning alignment.
    """
    try:
        payload = request.get_json() or {}
        records = payload.get('records', [])
        if isinstance(payload, dict) and 'raw_pm25' in payload:
            records = [payload]

        count = save_raw_telemetry_batch(records)
        return jsonify({"status": "success", "ingested_count": count})
    except Exception as e:
        print(f"Ingest telemetry error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@data_ingest_bp.route('/upload_reference', methods=['POST'])
def upload_reference():
    """
    Uploads new reference monitor CSV file, aligns with raw sensor logs on timestamp range,
    and executes continuous learning model retraining.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded in request."}), 400

        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"status": "error", "message": "No selected file."}), 400

        filename = file.filename
        content = file.read()

        # Parse CSV or Excel format
        if filename.endswith('.csv'):
            df_ref = pd.read_csv(io.BytesIO(content))
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df_ref = pd.read_excel(io.BytesIO(content))
        else:
            return jsonify({"status": "error", "message": "Unsupported file format. Please upload a .csv or .xlsx file."}), 400

        result = process_reference_upload_and_retrain(df_ref, filename=filename)
        return jsonify(result)
    except Exception as e:
        print(f"Upload reference error: {e}")
        return jsonify({"status": "error", "message": f"Retraining pipeline error: {str(e)}"}), 500

@data_ingest_bp.route('/retrain/history', methods=['GET'])
def get_retrain_history():
    """
    Fetches continuous learning retrain event logs from database.
    """
    try:
        logs = get_model_retrain_logs(limit=15)
        return jsonify({"status": "success", "history": logs})
    except Exception as e:
        print(f"Get retrain history error: {e}")
        return jsonify({"status": "error", "history": []}), 500
