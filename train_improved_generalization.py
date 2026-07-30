import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Step 1: Loading Training & Out-of-Sample Datasets ===")
project_dir = os.path.dirname(os.path.abspath(__file__))
train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

# Feature vector (14 Features including novel thermodynamic terms)
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

print(f"Training Samples: {len(train_df)} | Holdout Samples: {len(holdout_df)}")
print("-" * 60)

# 1. Regularized Random Forest (Depth Constrained & Leaf Regularized)
print("Training Regularized Random Forest (max_depth=10, min_samples_leaf=5)...")
rf_reg = RandomForestRegressor(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=5,
    max_features=0.8,
    random_state=42,
    n_jobs=-1
)
rf_reg.fit(X_train, y_train)

rf_preds = rf_reg.predict(X_holdout)
print(f"=== Regularized Random Forest (Unseen Holdout Performance) ===")
print(f"R² Score: {r2_score(y_holdout, rf_preds):.4f}")
print(f"MAE: {mean_absolute_error(y_holdout, rf_preds):.2f} µg/m³")
print(f"RMSE: {root_mean_squared_error(y_holdout, rf_preds):.2f} µg/m³")
print(f"Systematic Bias: {np.mean(rf_preds - y_holdout):+.2f} µg/m³")
print("-" * 60)

# 2. CatBoost Regressor (L2 Regularized & Symmetric Trees)
print("Training CatBoost Regressor with L2 Regularization...")
cb_reg = CatBoostRegressor(
    iterations=600,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=5.0,
    verbose=0,
    random_seed=42
)
cb_reg.fit(X_train, y_train)

cb_preds = cb_reg.predict(X_holdout)
print(f"=== CatBoost Regressor (Unseen Holdout Performance) ===")
print(f"R² Score: {r2_score(y_holdout, cb_preds):.4f}")
print(f"MAE: {mean_absolute_error(y_holdout, cb_preds):.2f} µg/m³")
print(f"RMSE: {root_mean_squared_error(y_holdout, cb_preds):.2f} µg/m³")
print(f"Systematic Bias: {np.mean(cb_preds - y_holdout):+.2f} µg/m³")
print("-" * 60)

# 3. LightGBM Regressor (Feature Subsampling & Min Child Samples)
print("Training LightGBM Regressor...")
lgb_reg = LGBMRegressor(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=7,
    num_leaves=31,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1
)
lgb_reg.fit(X_train, y_train)

lgb_preds = lgb_reg.predict(X_holdout)
print(f"=== LightGBM Regressor (Unseen Holdout Performance) ===")
print(f"R² Score: {r2_score(y_holdout, lgb_preds):.4f}")
print(f"MAE: {mean_absolute_error(y_holdout, lgb_preds):.2f} µg/m³")
print(f"RMSE: {root_mean_squared_error(y_holdout, lgb_preds):.2f} µg/m³")
print(f"Systematic Bias: {np.mean(lgb_preds - y_holdout):+.2f} µg/m³")
print("-" * 60)

# 4. Weighted Stacking Ensemble (CatBoost + LightGBM + Regularized RF)
ensemble_preds = 0.45 * cb_preds + 0.35 * lgb_preds + 0.20 * rf_preds
print(f"=== Weighted Stacking Ensemble (CatBoost + LightGBM + Regularized RF) ===")
print(f"R² Score: {r2_score(y_holdout, ensemble_preds):.4f}")
print(f"MAE: {mean_absolute_error(y_holdout, ensemble_preds):.2f} µg/m³")
print(f"RMSE: {root_mean_squared_error(y_holdout, ensemble_preds):.2f} µg/m³")
print(f"Systematic Bias: {np.mean(ensemble_preds - y_holdout):+.2f} µg/m³")
print("-" * 60)

# Save best generalization model
joblib.dump(cb_reg, os.path.join(project_dir, "models", "catboost_generalization_model.joblib"))
print("Saved CatBoost Generalization Model to models/catboost_generalization_model.joblib")
