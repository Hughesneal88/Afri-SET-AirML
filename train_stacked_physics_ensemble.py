import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from lightgbm import LGBMRegressor
from sklearn.linear_model import RidgeCV

def add_v4_physics_features(df):
    d = df.copy()
    temp = d['sample_temp']
    rh = d['sample_rh']
    pm25 = d['pm25']
    
    rh_clipped = np.clip(rh, 0.5, 99.8)
    rh_frac = rh_clipped / 100.0
    
    # Saturation Vapor Pressure e_s(T) in kPa (Tetens Formula)
    e_s = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    
    # Vapor Pressure Deficit (VPD) in kPa
    d['vpd'] = e_s * (1.0 - rh_frac)
    d['vapor_pressure_deficit'] = d['vpd']
    
    # Absolute Humidity (AH) in g/m³
    d['absolute_humidity'] = (216.7 * e_s * rh_frac) / (temp + 273.15)
    
    # Dew Point Temperature T_dew via Magnus formula
    gamma = ((17.27 * temp) / (237.3 + temp)) + np.log(rh_frac)
    d['dew_point'] = (237.3 * gamma) / (17.27 - gamma)
    d['dew_point_dep'] = temp - d['dew_point']
    d['dew_point_depression'] = d['dew_point_dep']
    
    # Kohler multi-gamma growth models
    for g in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]:
        d[f'kohler_gamma_{g}'] = pm25 * ((1.0 - rh_frac) ** g)
        
    d['rh_growth_ratio'] = rh_frac / (1.0 - rh_frac + 1e-4)
    d['pm25_kohler_scaled'] = pm25 / (1.0 + 0.15 * d['rh_growth_ratio'])
    d['rh_deliquescence_surge'] = np.where(rh_clipped > 75.0, np.exp((rh_clipped - 75.0) / 10.0), 0.0)
    
    # Multi-window EWMA & rolling stats
    for w in [1, 2, 3, 4, 6, 8, 12, 16, 24]:
        d[f'pm25_ewma_{w}'] = pm25.ewm(span=w, adjust=False).mean()
        d[f'pm25_roll_{w}_std'] = pm25.rolling(w, min_periods=1).std().fillna(0)
        d[f'pm25_roll_{w}_mean'] = pm25.rolling(w, min_periods=1).mean()
        d[f'pm25_roll_{w}_diff'] = pm25 - d[f'pm25_roll_{w}_mean']
        
    # Non-linear terms
    d['pm25_temp_interaction'] = pm25 * temp
    d['pm25_rh_interaction'] = pm25 * rh_clipped
    d['pm25_vpd_interaction'] = pm25 * d['vpd']
    d['temp_rh_ratio'] = temp / (rh_clipped + 1.0)
    d['log_pm25'] = np.log1p(np.maximum(pm25, 0))
    d['sqrt_pm25'] = np.sqrt(np.maximum(pm25, 0))
    
    # Temporal cycles
    if 'timestamp' in d.columns:
        d['timestamp'] = pd.to_datetime(d['timestamp'])
        month = d['timestamp'].dt.month
    else:
        month = 1
    if 'hour_of_day' not in d.columns:
        d['hour_of_day'] = 12
    if 'day_of_week' not in d.columns:
        d['day_of_week'] = 3

    d['hour_sin'] = np.sin(2 * np.pi * d['hour_of_day'] / 24.0)
    d['hour_cos'] = np.cos(2 * np.pi * d['hour_of_day'] / 24.0)
    d['day_sin'] = np.sin(2 * np.pi * d['day_of_week'] / 7.0)
    d['day_cos'] = np.cos(2 * np.pi * d['day_of_week'] / 7.0)
    d['month_sin'] = np.sin(2 * np.pi * month / 12.0)
    d['month_cos'] = np.cos(2 * np.pi * month / 12.0)
    
    return d

EXCLUDE_COLS = ['timestamp', 'PM25', 'pm25_env']

class StackedPhysicsMetaEnsemble:
    """
    Ultra High-Accuracy Stacked Physics-Informed Meta-Ensemble (SPIME v4) pipeline wrapper.
    """
    def __init__(self, m_rf, m_et, m_lgb, m_hgb, meta_model, feature_names):
        self.m_rf = m_rf
        self.m_et = m_et
        self.m_lgb = m_lgb
        self.m_hgb = m_hgb
        self.meta_model = meta_model
        self.feature_names = feature_names

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            df_in = X.copy()
            df_in = add_v4_physics_features(df_in)
            for c in self.feature_names:
                if c not in df_in.columns:
                    df_in[c] = 0.0
            X_input = df_in[self.feature_names]
        else:
            X_input = X

        p_rf = self.m_rf.predict(X_input)
        p_et = self.m_et.predict(X_input)
        p_lgb = self.m_lgb.predict(X_input)
        p_hgb = self.m_hgb.predict(X_input)

        S_input = np.column_stack([p_rf, p_et, p_lgb, p_hgb])
        return self.meta_model.predict(S_input)


if __name__ == '__main__':
    print("=== Training Ultra High-Accuracy Stacked Physics-Informed Meta-Ensemble (SPIME v4) ===")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    full_dataset_path = os.path.join(project_dir, "web_data", "full_dataset.csv")

    full_df = pd.read_csv(full_dataset_path).dropna(subset=['pm25', 'PM25'])
    data_feat = add_v4_physics_features(full_df)

    feature_cols = [c for c in data_feat.columns if c not in EXCLUDE_COLS]

    X = data_feat[feature_cols]
    y = data_feat['PM25'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.75, random_state=42)

    print(f"Training set: {len(X_train)} samples | Test set: {len(X_test)} samples | Features: {len(feature_cols)}")
    print("-" * 60)

    print("Fitting Base Estimators (RF, ExtraTrees, LightGBM, HistGradientBoosting)...")
    m_rf = RandomForestRegressor(n_estimators=120, max_depth=16, min_samples_split=2, min_samples_leaf=1, max_features=0.55, random_state=42, n_jobs=-1)
    m_et = ExtraTreesRegressor(n_estimators=120, max_depth=16, min_samples_split=2, min_samples_leaf=1, max_features=0.55, random_state=42, n_jobs=-1)
    m_lgb = LGBMRegressor(n_estimators=300, learning_rate=0.02, max_depth=12, num_leaves=120, min_child_samples=2, subsample=0.95, colsample_bytree=0.55, reg_alpha=0.005, reg_lambda=0.05, random_state=42, verbose=-1)
    m_hgb = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.02, max_depth=14, min_samples_leaf=2, l2_regularization=0.005, random_state=42)

    m_rf.fit(X_train, y_train)
    m_et.fit(X_train, y_train)
    m_lgb.fit(X_train, y_train)
    m_hgb.fit(X_train, y_train)

    print("Generating Out-of-Fold (OOF) Prediction Matrix via 5-Fold Cross-Validation...")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_rf = np.zeros(len(X_train))
    oof_et = np.zeros(len(X_train))
    oof_lgb = np.zeros(len(X_train))
    oof_hgb = np.zeros(len(X_train))

    for fold, (tr_idx, val_idx) in enumerate(kf.split(X_train), 1):
        X_tr_f, y_tr_f = X_train.iloc[tr_idx], y_train[tr_idx]
        X_val_f = X_train.iloc[val_idx]

        rf_f = RandomForestRegressor(n_estimators=80, max_depth=16, min_samples_split=2, min_samples_leaf=1, max_features=0.55, random_state=42, n_jobs=-1).fit(X_tr_f, y_tr_f)
        et_f = ExtraTreesRegressor(n_estimators=80, max_depth=16, min_samples_split=2, min_samples_leaf=1, max_features=0.55, random_state=42, n_jobs=-1).fit(X_tr_f, y_tr_f)
        lgb_f = LGBMRegressor(n_estimators=200, learning_rate=0.02, max_depth=12, num_leaves=120, min_child_samples=2, subsample=0.95, colsample_bytree=0.55, reg_alpha=0.005, reg_lambda=0.05, random_state=42, verbose=-1).fit(X_tr_f, y_tr_f)
        hgb_f = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.02, max_depth=14, min_samples_leaf=2, l2_regularization=0.005, random_state=42).fit(X_tr_f, y_tr_f)

        oof_rf[val_idx] = rf_f.predict(X_val_f)
        oof_et[val_idx] = et_f.predict(X_val_f)
        oof_lgb[val_idx] = lgb_f.predict(X_val_f)
        oof_hgb[val_idx] = hgb_f.predict(X_val_f)

    S_train = np.column_stack([oof_rf, oof_et, oof_lgb, oof_hgb])
    S_test = np.column_stack([m_rf.predict(X_test), m_et.predict(X_test), m_lgb.predict(X_test), m_hgb.predict(X_test)])

    print("Fitting RidgeCV Meta-Learner...")
    meta_model = RidgeCV(alphas=np.logspace(-4, 4, 30)).fit(S_train, y_train)

    train_preds = meta_model.predict(S_train)
    test_preds = meta_model.predict(S_test)

    train_r2 = r2_score(y_train, train_preds)
    test_r2 = r2_score(y_test, test_preds)
    test_mae = mean_absolute_error(y_test, test_preds)
    test_rmse = root_mean_squared_error(y_test, test_preds)
    bias = np.mean(test_preds - y_test)
    gap = train_r2 - test_r2

    print("=" * 60)
    print("=== SPIME v4 Performance ===")
    print(f"Train R² Score: {train_r2:.4f}")
    print(f"Test R² Score:  {test_r2:.4f}")
    print(f"MAE:           {test_mae:.2f} µg/m³")
    print(f"RMSE:          {test_rmse:.2f} µg/m³")
    print(f"Systematic Bias: {bias:+.2f} µg/m³")
    print(f"Overfitting Gap (Train R² - Test R²): {gap:.4f}")
    print("=" * 60)

    os.makedirs(os.path.join(project_dir, "models"), exist_ok=True)
    spime_pipeline = StackedPhysicsMetaEnsemble(m_rf, m_et, m_lgb, m_hgb, meta_model, feature_cols)
    
    out_model_path = os.path.join(project_dir, "models", "stacked_physics_meta_ensemble.joblib")
    root_model_path = os.path.join(project_dir, "stacked_physics_meta_ensemble.joblib")

    joblib.dump(spime_pipeline, out_model_path, compress=3)
    joblib.dump(spime_pipeline, root_model_path, compress=3)

    print(f"Successfully saved SPIME v4 model to:\n  - {out_model_path}\n  - {root_model_path}")

    print(f"Successfully saved SPIME v4 model to:\n  - {out_model_path}\n  - {root_model_path}")
