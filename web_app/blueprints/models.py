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
    from train_stacked_physics_ensemble import StackedPhysicsMetaEnsemble
    import sys
    sys.modules['__main__'].StackedPhysicsMetaEnsemble = StackedPhysicsMetaEnsemble
except Exception as e:
    print(f"SPIME import note: {e}")

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
        'holdout': os.path.join(PROJECT_DIR, 'web_data', 'out_of_sample_test.csv'),
        'validation': os.path.join(PROJECT_DIR, 'web_data', 'test_data.csv'),
        'test': os.path.join(PROJECT_DIR, 'web_data', 'test_data.csv'),
        'train': os.path.join(PROJECT_DIR, 'web_data', 'train_data.csv'),
        'full': os.path.join(PROJECT_DIR, 'web_data', 'full_dataset.csv')
    }
    
    target_path = path_map.get(partition, path_map['holdout'])
    if not os.path.exists(target_path):
        target_path = os.path.join(PROJECT_DIR, 'web_data', 'out_of_sample_test.csv')
        
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

    try:
        if hasattr(model, 'feature_names'):
            return model.predict(df)
        
        n_features = getattr(model, 'n_features_in_', model_info.get("features", 11))
        cols = Config.FEATURE_SETS.get(n_features, Config.FEATURE_SETS[11])
        
        # Fill any missing columns in dataset with 0.0 for safety
        X = df.copy()
        for col in cols:
            if col not in X.columns:
                X[col] = 0.0
        X_sub = X[cols]
        return model.predict(X_sub)
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

@models_bp.route('/predict', methods=['GET', 'POST'])
def predict_batch():
    try:
        if request.method == 'POST':
            payload = request.get_json() or {}
        else:
            payload = request.args.to_dict()
        model_key = payload.get('model_key', 'stacked_physics_meta_ensemble')
        raw_partition = (payload.get('partition') or payload.get('split') or 'holdout').lower()
        if raw_partition in ['val', 'validation']:
            partition = 'validation'
        elif raw_partition in ['test', 'holdout']:
            partition = 'holdout'
        elif raw_partition in ['all', 'full']:
            partition = 'full'
        else:
            partition = raw_partition
        compare_key = payload.get('compare_key', 'none')
        max_points = int(payload.get('max_points', 500))

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
        if compare_key != 'none':
            if compare_key == 'quantaq_factory':
                compare_predictions = run_model_inference('quantaq_factory', df, registry).tolist()
                compare_name = "QuantAQ Factory Uncalibrated Output"
            elif compare_key in registry:
                compare_predictions = run_model_inference(compare_key, df, registry).tolist()
                compare_name = registry[compare_key]["name"]

        timestamps = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist() if 'timestamp' in df.columns else list(range(len(df)))
        raw_pm25 = df['pm25'].tolist()
        actuals_list = actuals.tolist()
        preds_list = predictions.tolist()

        # Efficient downsampling for high-FPS chart rendering if dataset is large
        if max_points > 0 and len(df) > max_points:
            step = max(1, len(df) // max_points)
            timestamps_chart = timestamps[::step]
            actuals_chart = actuals_list[::step]
            preds_chart = preds_list[::step]
            raw_chart = raw_pm25[::step]
            compare_chart = compare_predictions[::step] if compare_predictions else []
        else:
            timestamps_chart = timestamps
            actuals_chart = actuals_list
            preds_chart = preds_list
            raw_chart = raw_pm25
            compare_chart = compare_predictions

        return jsonify({
            "status": "success",
            "model_key": model_key,
            "model_name": registry.get(model_key, {}).get("name", model_key),
            "compare_name": compare_name,
            "partition": partition,
            "timestamps": timestamps_chart,
            "actuals": actuals_chart,
            "predictions": preds_chart,
            "raw_pm25": raw_chart,
            "compare_predictions": compare_chart,
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

SYSTEM_SETTINGS = {
    "primary_model_key": "stacked_physics_meta_ensemble",
    "default_partition": "holdout",
    "max_points": 500,
    "refresh_interval": 15
}

@models_bp.route('/settings', methods=['GET', 'POST'])
def system_settings():
    global SYSTEM_SETTINGS
    if request.method == 'POST':
        payload = request.get_json() or {}
        if 'primary_model_key' in payload:
            SYSTEM_SETTINGS['primary_model_key'] = payload['primary_model_key']
        if 'default_partition' in payload:
            SYSTEM_SETTINGS['default_partition'] = payload['default_partition']
        if 'max_points' in payload:
            SYSTEM_SETTINGS['max_points'] = int(payload['max_points'])
        if 'refresh_interval' in payload:
            SYSTEM_SETTINGS['refresh_interval'] = int(payload['refresh_interval'])
        return jsonify({"status": "success", "message": "System settings saved successfully", "settings": SYSTEM_SETTINGS})
    
    return jsonify({"status": "success", "settings": SYSTEM_SETTINGS})

@models_bp.route('/live_telemetry', methods=['GET'])
def get_live_telemetry():
    try:
        from web_app.blueprints.views import quantaq_client
        model_key = request.args.get('model_key', SYSTEM_SETTINGS['primary_model_key'])
        telemetry = quantaq_client.calibrate_live_telemetry(model_key=model_key)
        return jsonify({"status": "success", "telemetry": telemetry})
    except Exception as e:
        print(f"Live telemetry endpoint error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/predict_single', methods=['POST'])
def predict_single():
    try:
        payload = request.get_json() or {}
        model_key = payload.get('model_key', SYSTEM_SETTINGS['primary_model_key'])
        
        pm25 = float(payload.get('pm25') or payload.get('raw_pm25') or 45.0)
        sample_temp = float(payload.get('sample_temp') or payload.get('temp') or 31.5)
        sample_rh = float(payload.get('sample_rh') or payload.get('rh') or 78.0)
        hour_of_day = int(payload.get('hour_of_day') if 'hour_of_day' in payload else (payload.get('hour') or 14))
        is_harmattan = int(payload.get('is_harmattan') if 'is_harmattan' in payload else (payload.get('harmattan_season') or 0))

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
