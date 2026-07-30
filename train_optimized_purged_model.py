import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

# Class Wrapper for Two-Stage Model
class TwoStagePurgedCalibrator:
    def __init__(self, primary_rf, residual_lgb):
        self.primary_rf = primary_rf
        self.residual_lgb = residual_lgb
        self.n_features_in_ = 8

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            cols = [
                'pm25', 'sample_temp', 'sample_rh', 'hour_of_day',
                'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
                'is_harmattan'
            ]
            X_input = X[cols].copy()
        else:
            X_input = X

        p_base = self.primary_rf.predict(X_input)
        e_est = self.residual_lgb.predict(X_input)
        return np.maximum(0.0, p_base + e_est)

if __name__ == '__main__':
    print("=== Step 1: Loading Data for Two-Stage Purged Calibration Pipeline ===")
    project_dir = os.path.dirname(os.path.abspath(__file__))

    train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
    holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

    cols = [
        'pm25', 'sample_temp', 'sample_rh', 'hour_of_day',
        'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
        'is_harmattan'
    ]

    X_train = train_df[cols]
    y_train = train_df['PM25'].values

    X_holdout = holdout_df[cols]
    y_holdout = holdout_df['PM25'].values

    print(f"Train Dataset: {len(X_train)} samples | Unseen Holdout: {len(X_holdout)} samples")
    print("-" * 60)

    print("--- Step 2: Fitting Primary Purged Random Forest Model ---")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = []

    for fold, (t_idx, v_idx) in enumerate(tscv.split(X_train)):
        X_tr, y_tr = X_train.iloc[t_idx], y_train[t_idx]
        X_va, y_va = X_train.iloc[v_idx], y_train[v_idx]
        
        rf_temp = RandomForestRegressor(
            n_estimators=250,
            max_depth=12,
            min_samples_leaf=4,
            max_features=0.75,
            random_state=42,
            n_jobs=-1
        )
        rf_temp.fit(X_tr, y_tr)
        val_pred = rf_temp.predict(X_va)
        score = r2_score(y_va, val_pred)
        cv_scores.append(score)
        print(f"Time-Series CV Fold {fold+1} R²: {score:.4f}")

    print(f"Mean Purged Time-Series CV R²: {np.mean(cv_scores):.4f}")
    print("-" * 60)

    primary_rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=4,
        max_features=0.75,
        random_state=42,
        n_jobs=-1
    )
    primary_rf.fit(X_train, y_train)

    primary_train_preds = primary_rf.predict(X_train)
    train_residuals = y_train - primary_train_preds

    print("--- Step 3: Fitting Stage-2 Residual Error Corrector ---")
    residual_corrector = LGBMRegressor(
        n_estimators=150,
        learning_rate=0.02,
        max_depth=5,
        num_leaves=15,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=5.0,
        random_state=42,
        verbose=-1
    )
    residual_corrector.fit(X_train, train_residuals)

    print("--- Step 4: Evaluating Two-Stage Model on Unseen Holdout Dataset ---")
    primary_holdout_preds = primary_rf.predict(X_holdout)
    estimated_residuals = residual_corrector.predict(X_holdout)

    final_holdout_preds = np.maximum(0.0, primary_holdout_preds + estimated_residuals)

    r2_stage1 = r2_score(y_holdout, primary_holdout_preds)
    r2_final = r2_score(y_holdout, final_holdout_preds)
    mae_final = mean_absolute_error(y_holdout, final_holdout_preds)
    rmse_final = root_mean_squared_error(y_holdout, final_holdout_preds)
    bias_final = np.mean(final_holdout_preds - y_holdout)

    print(f"Stage-1 Primary RF Holdout R²: {r2_stage1:.4f}")
    print(f"=== Stage-2 Final Corrected Model (Unseen Holdout Performance) ===")
    print(f"Unseen Holdout R² Score: {r2_final:.4f}")
    print(f"MAE: {mae_final:.2f} µg/m³")
    print(f"RMSE: {rmse_final:.2f} µg/m³")
    print(f"Systematic Bias: {bias_final:+.2f} µg/m³")
    print("-" * 60)

    two_stage_model = TwoStagePurgedCalibrator(primary_rf, residual_corrector)
    os.makedirs("models", exist_ok=True)
    model_path = os.path.join(project_dir, "models", "two_stage_purged_calibrator.joblib")
    joblib.dump(two_stage_model, model_path)
    print(f"Saved Two-Stage Purged Calibrator to: {model_path}")
