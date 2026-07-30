import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from train_moe_expert import AtmosphericMoE

print("=== Evaluating Models on True Unseen Out-of-Sample Holdout Dataset ===")
project_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv"))
df = df.dropna(subset=['pm25', 'PM25'])

actuals = df['PM25'].values
raw_sensor = df['pm25'].values

print(f"Total Unseen Holdout Records: {len(df)} samples")
print(f"Time Horizon: {df['timestamp'].min()} to {df['timestamp'].max()}")
print("-" * 60)

# Raw Sensor Metrics (Uncalibrated)
raw_r2 = r2_score(actuals, raw_sensor)
raw_mae = mean_absolute_error(actuals, raw_sensor)
raw_rmse = root_mean_squared_error(actuals, raw_sensor)
raw_bias = np.mean(raw_sensor - actuals)
print(f"=== QuantAQ Factory Default (Uncalibrated Raw Sensor) ===")
print(f"R² Score: {raw_r2:.4f}")
print(f"MAE: {raw_mae:.2f} µg/m³")
print(f"RMSE: {raw_rmse:.2f} µg/m³")
print(f"Systematic Bias: {raw_bias:+.2f} µg/m³")
print("-" * 60)

cols11 = [
    'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
    'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
    'is_harmattan_month', 'harmattan_score', 'is_harmattan'
]

cols14 = cols11 + ['vapor_pressure_deficit', 'dew_point_depression', 'rh_deliquescence_surge']

models = {
    'Random Forest Regressor (v2 Best Model)': 'random_forest_pm25_model_update2.joblib',
    'Atmospheric Mixture of Experts (MoE)': 'models/moe_expert_model.joblib',
    'Deep Neural LLM Regressor': 'models/llm_calibration_model.joblib',
    'MLP Neural Network Regressor': 'models/mlp_neural_network.joblib',
    'Multiple Linear Regression (Baseline)': 'models/linear_regression_baseline.joblib'
}

for name, path in models.items():
    file_path = os.path.join(project_dir, path)
    if os.path.exists(file_path):
        m = joblib.load(file_path)
        feature_cols = cols14 if "moe" in path else cols11
        preds = m.predict(df[feature_cols])
        
        r2 = r2_score(actuals, preds)
        mae = mean_absolute_error(actuals, preds)
        rmse = root_mean_squared_error(actuals, preds)
        bias = np.mean(preds - actuals)
        
        print(f"=== {name} ===")
        print(f"R² Score: {r2:.4f}")
        print(f"MAE: {mae:.2f} µg/m³")
        print(f"RMSE: {rmse:.2f} µg/m³")
        print(f"Systematic Bias: {bias:+.2f} µg/m³")
        print("-" * 60)
