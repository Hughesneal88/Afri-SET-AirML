import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Training Compact Non-Overfitting Random Forest ===")
project_dir = os.path.dirname(os.path.abspath(__file__))
train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

# Non-collinear compact feature set (6 features)
compact_cols = [
    'pm25', 'sample_temp', 'sample_rh', 'hour_of_day',
    'rolling_mean_pm25', 'is_harmattan'
]

X_train = train_df[compact_cols]
y_train = train_df['PM25'].values

X_holdout = holdout_df[compact_cols]
y_holdout = holdout_df['PM25'].values

# Fit Compact Regularized Random Forest
compact_rf = RandomForestRegressor(
    n_estimators=250,
    max_depth=8,
    min_samples_leaf=10,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)

compact_rf.fit(X_train, y_train)

train_preds = compact_rf.predict(X_train)
train_r2 = r2_score(y_train, train_preds)

holdout_preds = compact_rf.predict(X_holdout)
holdout_r2 = r2_score(y_holdout, holdout_preds)
mae = mean_absolute_error(y_holdout, holdout_preds)
rmse = root_mean_squared_error(y_holdout, holdout_preds)

print(f"Compact Model Train R²: {train_r2:.4f}")
print(f"=== Compact RF Holdout Generalization Metrics (3,468 Unseen Samples) ===")
print(f"Unseen Holdout R² Score: {holdout_r2:.4f}")
print(f"MAE: {mae:.2f} µg/m³")
print(f"RMSE: {rmse:.2f} µg/m³")
print(f"Generalization Gap (Train - Holdout): {train_r2 - holdout_r2:.4f}")

model_path = os.path.join(project_dir, "models", "compact_generalization_rf.joblib")
joblib.dump(compact_rf, model_path)
print(f"Saved Compact RF model to: {model_path}")
