import os
import pandas as pd
import numpy as np
import joblib
from lightgbm import LGBMRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Training Non-Overfitting LightGBM Model ===")
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

# Fit Non-Overfitting Regularized LightGBM Regressor
lgb_model = LGBMRegressor(
    n_estimators=350,
    learning_rate=0.03,
    max_depth=6,
    num_leaves=25,
    min_child_samples=35,
    subsample=0.8,
    colsample_bytree=0.7,
    reg_alpha=1.0,
    reg_lambda=5.0,
    random_state=42,
    verbose=-1
)

lgb_model.fit(X_train, y_train)

# Evaluate on Training Set
train_preds = lgb_model.predict(X_train)
train_r2 = r2_score(y_train, train_preds)

# Evaluate on Unseen Holdout Set
holdout_preds = lgb_model.predict(X_holdout)
r2 = r2_score(y_holdout, holdout_preds)
mae = mean_absolute_error(y_holdout, holdout_preds)
rmse = root_mean_squared_error(y_holdout, holdout_preds)
bias = np.mean(holdout_preds - y_holdout)

print(f"Train R²: {train_r2:.4f}")
print(f"=== LightGBM Holdout Generalization Metrics (3,468 Unseen Samples) ===")
print(f"Unseen Holdout R² Score: {r2:.4f}")
print(f"MAE: {mae:.2f} µg/m³")
print(f"RMSE: {rmse:.2f} µg/m³")
print(f"Systematic Bias: {bias:+.2f} µg/m³")
print(f"Generalization Gap (Train R² - Holdout R²): {train_r2 - r2:.4f}")

model_path = os.path.join(project_dir, "models", "lightgbm_generalization_model.joblib")
joblib.dump(lgb_model, model_path)
print(f"Saved Non-Overfitting LightGBM model to: {model_path}")
