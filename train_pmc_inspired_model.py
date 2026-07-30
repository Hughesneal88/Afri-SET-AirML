import os
import pandas as pd
import numpy as np
import joblib
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

# Class wrapper for joblib persistence
class PMCHybridCalibrator:
    def __init__(self, knn_pipe, gbr, rf):
        self.knn_pipe = knn_pipe
        self.gbr = gbr
        self.rf = rf
        self.n_features_in_ = 10

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X_df = X.copy()
            if 'pm25_smoothed' not in X_df.columns:
                X_df['pm25_smoothed'] = X_df['pm25'].rolling(window=10, min_periods=1).mean()
            cols = [
                'pm25_smoothed', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
                'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
                'vapor_pressure_deficit', 'is_harmattan'
            ]
            if 'vapor_pressure_deficit' not in X_df.columns:
                X_df['vapor_pressure_deficit'] = X_df['sample_temp'] * (1 - X_df['sample_rh']/100)
            X_input = X_df[cols]
        else:
            X_input = X

        p_knn = self.knn_pipe.predict(X_input)
        p_gbr = self.gbr.predict(X_input)
        p_rf = self.rf.predict(X_input)

        return 0.40 * p_rf + 0.35 * p_knn + 0.25 * p_gbr

def preprocess_pmc_features(df):
    X_df = df.copy()
    X_df['pm25_smoothed'] = X_df['pm25'].rolling(window=10, min_periods=1).mean()
    X_df['pm25_rh_interaction'] = X_df['pm25_smoothed'] * X_df['sample_rh']
    X_df['vapor_pressure_deficit'] = X_df['vapor_pressure_deficit'] if 'vapor_pressure_deficit' in X_df.columns else X_df['sample_temp'] * (1 - X_df['sample_rh']/100)
    
    cols = [
        'pm25_smoothed', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
        'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
        'vapor_pressure_deficit', 'is_harmattan'
    ]
    return X_df[cols]

if __name__ == '__main__':
    print("=== Training PMC12115728-Inspired Hybrid kNN-GBR-RF Calibration Model ===")
    project_dir = os.path.dirname(os.path.abspath(__file__))

    train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
    holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

    X_train = preprocess_pmc_features(train_df)
    y_train = train_df['PM25'].values

    X_holdout = preprocess_pmc_features(holdout_df)
    y_holdout = holdout_df['PM25'].values

    print(f"Training Dataset: {len(X_train)} samples | Holdout Dataset: {len(X_holdout)} samples")
    print("-" * 60)

    # Model 1: k-Nearest Neighbors Regressor
    knn_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('knn', KNeighborsRegressor(n_neighbors=20, weights='distance', metric='euclidean', n_jobs=-1))
    ])
    knn_pipeline.fit(X_train, y_train)
    knn_preds = knn_pipeline.predict(X_holdout)

    print("=== 1. k-Nearest Neighbors (kNN) Holdout Performance ===")
    print(f"Holdout R²: {r2_score(y_holdout, knn_preds):.4f}")
    print(f"MAE: {mean_absolute_error(y_holdout, knn_preds):.2f} µg/m³")
    print(f"RMSE: {root_mean_squared_error(y_holdout, knn_preds):.2f} µg/m³")
    print("-" * 60)

    # Model 2: Gradient Boosting Regressor (GBR)
    gbr_model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=6,
        subsample=0.8,
        max_features=0.8,
        random_state=42
    )
    gbr_model.fit(X_train, y_train)
    gbr_preds = gbr_model.predict(X_holdout)

    print("=== 2. Gradient Boosting Regressor (GBR) Holdout Performance ===")
    print(f"Holdout R²: {r2_score(y_holdout, gbr_preds):.4f}")
    print(f"MAE: {mean_absolute_error(y_holdout, gbr_preds):.2f} µg/m³")
    print(f"RMSE: {root_mean_squared_error(y_holdout, gbr_preds):.2f} µg/m³")
    print("-" * 60)

    # Model 3: Random Forest Regressor
    rf_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_holdout)

    print("=== 3. Random Forest (RF) Holdout Performance ===")
    print(f"Holdout R²: {r2_score(y_holdout, rf_preds):.4f}")
    print(f"MAE: {mean_absolute_error(y_holdout, rf_preds):.2f} µg/m³")
    print(f"RMSE: {root_mean_squared_error(y_holdout, rf_preds):.2f} µg/m³")
    print("-" * 60)

    # Model 4: Hybrid Stacking Ensemble
    ensemble_preds = 0.40 * rf_preds + 0.35 * knn_preds + 0.25 * gbr_preds

    print("=== 4. Hybrid PMC Ensemble (kNN + GBR + RF + Pre-Smoothing) ===")
    print(f"Holdout R² Score: {r2_score(y_holdout, ensemble_preds):.4f}")
    print(f"MAE: {mean_absolute_error(y_holdout, ensemble_preds):.2f} µg/m³")
    print(f"RMSE: {root_mean_squared_error(y_holdout, ensemble_preds):.2f} µg/m³")
    print(f"Systematic Bias: {np.mean(ensemble_preds - y_holdout):+.2f} µg/m³")
    print("-" * 60)

    hybrid_model = PMCHybridCalibrator(knn_pipeline, gbr_model, rf_model)
    os.makedirs("models", exist_ok=True)
    model_path = os.path.join(project_dir, "models", "pmc_hybrid_calibrator.joblib")
    joblib.dump(hybrid_model, model_path)
    print(f"Saved PMC Hybrid Calibrator to: {model_path}")
