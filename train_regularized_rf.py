import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Training Regularized Random Forest for Unseen Generalization ===")
project_dir = os.path.dirname(os.path.abspath(__file__))
train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

cols = [
    'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
    'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
    'vapor_pressure_deficit', 'dew_point_depression', 'rh_deliquescence_surge',
    'is_harmattan_month', 'harmattan_score', 'is_harmattan'
]

X_train = train_df[cols]
y_train = train_df['PM25'].values

X_holdout = holdout_df[cols]
y_holdout = holdout_df['PM25'].values

# Fit Regularized Random Forest (max_depth=10, min_samples_leaf=5)
rf_reg = RandomForestRegressor(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=5,
    max_features=0.8,
    random_state=42,
    n_jobs=-1
)
rf_reg.fit(X_train, y_train)

preds = rf_reg.predict(X_holdout)
r2 = r2_score(y_holdout, preds)
mae = mean_absolute_error(y_holdout, preds)
rmse = root_mean_squared_error(y_holdout, preds)
bias = np.mean(preds - y_holdout)

print(f"=== Regularized Random Forest Performance on Unseen Holdout ===")
print(f"R² Score: {r2:.4f}")
print(f"MAE: {mae:.2f} µg/m³")
print(f"RMSE: {rmse:.2f} µg/m³")
print(f"Systematic Bias: {bias:+.2f} µg/m³")

model_path = os.path.join(project_dir, "models", "random_forest_regularized.joblib")
joblib.dump(rf_reg, model_path)
print(f"Saved regularized model to: {model_path}")
