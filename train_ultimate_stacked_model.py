import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Building Ultimate Köhler-Ensemble Calibration Model ===")
project_dir = os.path.dirname(os.path.abspath(__file__))

train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

def apply_kohler_precorrection(df):
    X_df = df.copy()
    rh = np.clip(X_df['sample_rh'], 0.0, 98.0)
    kappa = 0.22  # Empirical kappa for coastal West African aerosols
    
    # Köhler physical dry mass estimation
    growth_factor = 1.0 + kappa * (rh / (100.0 - rh + 1e-5))
    X_df['pm25_kohler_dry'] = X_df['pm25'] / (growth_factor ** (1.0/3.0))
    X_df['pm25_rh_interaction'] = X_df['pm25_kohler_dry'] * rh
    X_df['rolling_mean_pm25'] = X_df['pm25_kohler_dry'].rolling(window=3, min_periods=1).mean()
    
    cols = [
        'pm25_kohler_dry', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
        'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
        'is_harmattan_month', 'harmattan_score', 'is_harmattan'
    ]
    return X_df[cols]

X_train = apply_kohler_precorrection(train_df)
y_train = train_df['PM25'].values

X_holdout = apply_kohler_precorrection(holdout_df)
y_holdout = holdout_df['PM25'].values

print(f"Training Samples: {len(X_train)} | Unseen Holdout Samples: {len(X_holdout)}")
print("-" * 60)

# Model 1: Tuned Random Forest
rf_opt = RandomForestRegressor(
    n_estimators=350,
    max_depth=12,
    min_samples_leaf=3,
    max_features=0.8,
    random_state=42,
    n_jobs=-1
)
rf_opt.fit(X_train, y_train)
rf_preds = rf_opt.predict(X_holdout)

# Model 2: Regularized LightGBM
lgb_opt = LGBMRegressor(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=6,
    num_leaves=25,
    min_child_samples=25,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.5,
    reg_lambda=3.0,
    random_state=42,
    verbose=-1
)
lgb_opt.fit(X_train, y_train)
lgb_preds = lgb_opt.predict(X_holdout)

# Stacking Blend: 60% RF + 40% LightGBM
ensemble_preds = 0.60 * rf_preds + 0.40 * lgb_preds

r2 = r2_score(y_holdout, ensemble_preds)
mae = mean_absolute_error(y_holdout, ensemble_preds)
rmse = root_mean_squared_error(y_holdout, ensemble_preds)
bias = np.mean(ensemble_preds - y_holdout)

print(f"=== Ultimate Köhler-Ensemble (Unseen Holdout Generalization) ===")
print(f"Unseen Holdout R² Score: {r2:.4f}")
print(f"MAE: {mae:.2f} µg/m³")
print(f"RMSE: {rmse:.2f} µg/m³")
print(f"Systematic Bias: {bias:+.2f} µg/m³")
print("-" * 60)

class UltimateKohlerEnsemble:
    def __init__(self, rf, lgb):
        self.rf = rf
        self.lgb = lgb
        self.n_features_in_ = 11

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X_df = X.copy()
            if 'pm25_kohler_dry' not in X_df.columns:
                rh = np.clip(X_df['sample_rh'], 0.0, 98.0)
                growth_factor = 1.0 + 0.22 * (rh / (100.0 - rh + 1e-5))
                X_df['pm25_kohler_dry'] = X_df['pm25'] / (growth_factor ** (1.0/3.0))
                X_df['pm25_rh_interaction'] = X_df['pm25_kohler_dry'] * rh
                X_df['rolling_mean_pm25'] = X_df['pm25_kohler_dry'].rolling(window=3, min_periods=1).mean()
            cols = [
                'pm25_kohler_dry', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
                'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
                'is_harmattan_month', 'harmattan_score', 'is_harmattan'
            ]
            X_input = X_df[cols]
        else:
            X_input = X

        p_rf = self.rf.predict(X_input)
        p_lgb = self.lgb.predict(X_input)
        return 0.60 * p_rf + 0.40 * p_lgb

ultimate_model = UltimateKohlerEnsemble(rf_opt, lgb_opt)
os.makedirs("models", exist_ok=True)
model_path = os.path.join(project_dir, "models", "ultimate_kohler_ensemble.joblib")
joblib.dump(ultimate_model, model_path)
print(f"Saved Ultimate Köhler Ensemble to: {model_path}")
