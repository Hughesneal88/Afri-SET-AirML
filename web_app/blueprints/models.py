import os
import sys
import glob
import pandas as pd
import numpy as np
import joblib
from flask import Blueprint, request, jsonify
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from web_app.config import Config
from web_app.rag_engine import AirQualityRAGEngine

models_bp = Blueprint('models', __name__, url_prefix='/api')
rag_engine = AirQualityRAGEngine(BASE_DIR)

loaded_models_cache = {}

# Custom model wrappers for pickle loading
try:
    from train_moe_expert import AtmosphericMoE
except Exception:
    pass

try:
    from train_pmc_inspired_model import PMCHybridCalibrator
except Exception:
    pass

try:
    from train_optimized_purged_model import TwoStagePurgedCalibrator
except Exception:
    pass

def discover_joblib_models():
    registry = {}
    search_dirs = [BASE_DIR, PROJECT_DIR, os.path.join(PROJECT_DIR, 'models')]
    
    found_files = {}
    for d in search_dirs:
        if os.path.exists(d):
            for file_path in glob.glob(os.path.join(d, "*.joblib")):
                fname = os.path.basename(file_path)
                found_files[fname] = file_path

    for key, config in Config.DISTINCT_MODEL_CONFIG.items():
        chosen_path = None
        for fn in config["file_names"]:
            if fn in found_files:
                chosen_path = found_files[fn]
                break
        
        if chosen_path:
            registry[key] = {
                "name": config["name"],
                "file": chosen_path,
                "features": config["features"]
            }

    if not registry and found_files:
        for fname, fpath in found_files.items():
            key = fname.replace(".joblib", "").lower()
            registry[key] = {
                "name": fname.replace(".joblib", "").replace("_", " ").title(),
                "file": fpath,
                "features": 11
            }

    return registry

def get_model_from_file(file_path):
    if file_path in loaded_models_cache:
        return loaded_models_cache[file_path]
    try:
        model = joblib.load(file_path)
        loaded_models_cache[file_path] = model
        return model
    except Exception as e:
        print(f"Model load exception ({file_path}): {e}")
        return None

def load_dataset_split(partition='holdout'):
    path_map = {
        'holdout': os.path.join(BASE_DIR, 'web_data', 'holdout_data.csv'),
        'validation': os.path.join(BASE_DIR, 'web_data', 'val_data.csv'),
        'test': os.path.join(BASE_DIR, 'web_data', 'test_data.csv'),
        'full': os.path.join(BASE_DIR, 'web_data', 'full_dataset.csv')
    }
    
    target_path = path_map.get(partition, path_map['holdout'])
    if not os.path.exists(target_path):
        target_path = os.path.join(PROJECT_DIR, 'web_data', 'full_dataset.csv')
        
    if os.path.exists(target_path):
        df = pd.read_csv(target_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df.dropna(subset=['pm25', 'PM25'])
    
    return pd.DataFrame()

def run_model_inference(model_key, df, registry):
    if model_key == 'quantaq_factory':
        return df['pm25_env'].values if 'pm25_env' in df.columns else df['pm25'].values

    model_info = registry.get(model_key)
    if not model_info or not model_info["file"]:
        return df['pm25'].values

    model = get_model_from_file(model_info["file"])
    if model is None:
        return df['pm25'].values

    n_features = getattr(model, 'n_features_in_', model_info.get("features", 11))
    cols = Config.FEATURE_SETS.get(n_features, Config.FEATURE_SETS[11])

    try:
        X = df[cols].copy()
        return model.predict(X)
    except Exception as e:
        print(f"Inference error for model {model_key}: {e}")
        return df['pm25'].values

@models_bp.route('/models', methods=['GET'])
def get_models():
    registry = discover_joblib_models()
    models_list = []
    for key, info in registry.items():
        models_list.append({
            "key": key,
            "name": info["name"],
            "features": info["features"]
        })
    return jsonify({"status": "success", "models": models_list})

@models_bp.route('/predict', methods=['POST'])
def predict_batch():
    try:
        payload = request.get_json() or {}
        model_key = payload.get('model_key', 'random_forest_pm25_model_update2')
        partition = payload.get('partition', 'holdout')
        compare_key = payload.get('compare_key', 'none')

        df = load_dataset_split(partition)
        if df.empty:
            return jsonify({"status": "error", "message": f"Partition {partition} empty"}), 400

        registry = discover_joblib_models()
        predictions = run_model_inference(model_key, df, registry)

        actuals = df['PM25'].values
        r2 = float(r2_score(actuals, predictions))
        mae = float(mean_absolute_error(actuals, predictions))
        rmse = float(root_mean_squared_error(actuals, predictions))
        bias = float(np.mean(predictions - actuals))

        compare_predictions = []
        compare_name = ""
        if compare_key != 'none' and compare_key in registry:
            compare_predictions = run_model_inference(compare_key, df, registry).tolist()
            compare_name = registry[compare_key]["name"]

        timestamps = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist() if 'timestamp' in df.columns else list(range(len(df)))
        raw_pm25 = df['pm25'].tolist()

        return jsonify({
            "status": "success",
            "model_key": model_key,
            "model_name": registry.get(model_key, {}).get("name", model_key),
            "compare_name": compare_name,
            "partition": partition,
            "timestamps": timestamps,
            "actuals": actuals.tolist(),
            "predictions": predictions.tolist(),
            "raw_pm25": raw_pm25,
            "compare_predictions": compare_predictions,
            "metrics": {
                "r2": r2,
                "mae": mae,
                "rmse": rmse,
                "bias": bias,
                "sample_count": len(df)
            }
        })
    except Exception as e:
        print(f"Predict batch error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/predict_single', methods=['POST'])
def predict_single():
    try:
        payload = request.get_json() or {}
        model_key = payload.get('model_key', 'random_forest_pm25_model_update2')
        
        pm25 = float(payload.get('pm25', 45.0))
        sample_temp = float(payload.get('sample_temp', 31.5))
        sample_rh = float(payload.get('sample_rh', 78.0))
        hour_of_day = int(payload.get('hour_of_day', 14))
        is_harmattan = int(payload.get('is_harmattan', 0))

        registry = discover_joblib_models()
        model_info = registry.get(model_key)
        model = get_model_from_file(model_info["file"]) if model_info and model_info["file"] else None
        model_name = model_info.get("name", model_key) if model_info else model_key

        rag_result = rag_engine.calibrate_and_explain(
            model=model,
            model_name=model_name,
            raw_pm25=pm25,
            temp=sample_temp,
            rh=sample_rh,
            hour=hour_of_day,
            is_harmattan=is_harmattan
        )

        return jsonify({
            "status": "success",
            "prediction": rag_result["numeric_values"]["calibrated_pm25"],
            "rag": rag_result
        })
    except Exception as e:
        print(f"Predict single error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
