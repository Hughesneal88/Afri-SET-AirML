import os
import pandas as pd
import numpy as np
import joblib

# Forecaster Class Definition
class AirQuality24hForecaster:
    def __init__(self, model, horizon_sigmas, lags):
        self.model = model
        self.horizon_sigmas = horizon_sigmas
        self.lags = lags
        self.feature_count = 25

    def extract_features(self, history_df):
        """
        history_df must have at least 24 recent hourly records with columns:
        ['PM25' or 'pm25', 'sample_temp', 'sample_rh']
        """
        df_sorted = history_df.copy()
        if 'timestamp' in df_sorted.columns:
            df_sorted['timestamp'] = pd.to_datetime(df_sorted['timestamp'])
            df_sorted = df_sorted.sort_values('timestamp').reset_index(drop=True)
            
        target_col = 'PM25' if 'PM25' in df_sorted.columns and not df_sorted['PM25'].isna().all() else 'pm25'
        vals = df_sorted[target_col].values
        
        if len(vals) < 24:
            raise ValueError(f"Forecaster requires at least 24 historical hours, got {len(vals)}")
            
        y_past = [float(vals[-1 - l]) for l in self.lags]
        
        y_roll_mean_6 = float(np.mean(vals[-6:]))
        y_roll_std_6 = float(np.std(vals[-6:]))
        y_roll_mean_24 = float(np.mean(vals[-24:]))
        y_roll_std_24 = float(np.std(vals[-24:]))
        y_min_24 = float(np.min(vals[-24:]))
        y_max_24 = float(np.max(vals[-24:]))
        
        last_row = df_sorted.iloc[-1]
        temp = float(last_row.get('sample_temp', 28.0))
        rh = float(last_row.get('sample_rh', 75.0))
        vpd = float(last_row.get('vapor_pressure_deficit', 0.61078 * np.exp((17.27 * temp)/(temp + 237.3)) * (1.0 - rh/100.0)))
        dp_dep = float(last_row.get('dew_point_depression', temp - (temp - ((100.0 - rh)/5.0))))
        surge = float(last_row.get('rh_deliquescence_surge', np.exp((rh - 75.0)/10.0) if rh > 75.0 else 0.0))
        harm = float(last_row.get('harmattan_score', 0.0))
        is_harm = int(last_row.get('is_harmattan', 0))
        
        if 'timestamp' in last_row:
            cur_time = pd.to_datetime(last_row['timestamp'])
            hr = cur_time.hour
            dow = cur_time.dayofweek
            month = cur_time.month
        else:
            hr = 12
            dow = 2
            month = 1
            
        hr_sin = np.sin(2 * np.pi * hr / 24.0)
        hr_cos = np.cos(2 * np.pi * hr / 24.0)
        dow_sin = np.sin(2 * np.pi * dow / 7.0)
        dow_cos = np.cos(2 * np.pi * dow / 7.0)
        month_sin = np.sin(2 * np.pi * month / 12.0)
        month_cos = np.cos(2 * np.pi * month / 12.0)
        
        feats = y_past + [
            y_roll_mean_6, y_roll_std_6, y_roll_mean_24, y_roll_std_24, y_min_24, y_max_24,
            temp, rh, vpd, dp_dep, surge, harm, is_harm,
            hr_sin, hr_cos, dow_sin, dow_cos, month_sin, month_cos
        ]
        return np.array([feats])

    def forecast_24h(self, history_df, now_anchor=None):
        X_in = self.extract_features(history_df)
        if hasattr(self.model, 'estimators_'):
            preds = np.array([float(est.predict(X_in)[0]) for est in self.model.estimators_])
        else:
            if hasattr(self.model, 'n_jobs'):
                self.model.n_jobs = 1
            preds = self.model.predict(X_in)[0]
        # Guarantee non-negative concentrations
        preds = np.maximum(0.5, preds)

        # Always anchor forecast timestamps to the current wall-clock hour,
        # so +1h = upcoming hour, +24h = 24h ahead from the current live period.
        if now_anchor is not None:
            now_h = pd.to_datetime(now_anchor).floor('h')
        elif 'timestamp' in history_df.columns and not history_df['timestamp'].empty:
            now_h = pd.to_datetime(history_df.iloc[-1]['timestamp']).floor('h')
        else:
            now_h = pd.Timestamp.now().floor('h')

        target_col = 'PM25' if 'PM25' in history_df.columns and not history_df['PM25'].isna().all() else 'pm25'
        live_y0 = float(history_df.iloc[-1][target_col])

        # Operational forecast data assimilation / persistence relaxation:
        # Smoothly transitions from the exact live current reading into the multi-horizon LightGBM trajectory
        initial_step_diff = live_y0 - float(preds[0])

        hourly_results = []
        for h in range(len(preds)):
            raw_pred_h = float(preds[h])
            # Smooth exponential decay of the initial difference towards pure model physics
            nudge = initial_step_diff * np.exp(-(h + 1) / 3.0)
            pred_h = max(0.5, raw_pred_h + nudge)

            sigma_h = float(self.horizon_sigmas[h]) if h < len(self.horizon_sigmas) else 5.0
            margin = 1.645 * sigma_h  # 90% confidence interval
            lower_b = max(0.0, pred_h - margin)
            upper_b = pred_h + margin
            future_ts = now_h + pd.Timedelta(hours=h + 1)

            hourly_results.append({
                "horizon": h + 1,
                "timestamp": future_ts.strftime('%Y-%m-%d %H:%M:%S'),
                "hour_label": future_ts.strftime('%H:00'),
                "pm25": round(pred_h, 2),
                "lower_bound": round(lower_b, 2),
                "upper_bound": round(upper_b, 2)
            })

        return hourly_results


if __name__ == '__main__':
    from sklearn.multioutput import MultiOutputRegressor
    from lightgbm import LGBMRegressor
    from sklearn.metrics import mean_absolute_error, r2_score

    print("=== Training Multi-Horizon 24-Hour Air Quality Forecaster ===")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(project_dir, "web_data", "full_dataset.csv")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    target = df['PM25'].values
    N = len(df)
    HORIZONS = 24
    LAGS = [0, 1, 2, 3, 5, 11, 23]

    print(f"Total time-series length: {N} hourly records ({df['timestamp'].min()} to {df['timestamp'].max()})")

    X_list = []
    Y_list = []

    for i in range(24, N - HORIZONS):
        y_past = [target[i - l] for l in LAGS]
        y_roll_mean_6 = np.mean(target[i-5:i+1])
        y_roll_std_6 = np.std(target[i-5:i+1])
        y_roll_mean_24 = np.mean(target[i-23:i+1])
        y_roll_std_24 = np.std(target[i-23:i+1])
        y_min_24 = np.min(target[i-23:i+1])
        y_max_24 = np.max(target[i-23:i+1])
        
        cur_t = df.iloc[i]
        temp = cur_t['sample_temp']
        rh = cur_t['sample_rh']
        vpd = cur_t.get('vapor_pressure_deficit', 0.61 * (1 - rh/100.0))
        dp_dep = cur_t.get('dew_point_depression', temp - (temp - (100 - rh)/5))
        surge = cur_t.get('rh_deliquescence_surge', 0.0)
        harm = cur_t.get('harmattan_score', 0.0)
        is_harm = cur_t.get('is_harmattan', 0)
        
        hr = cur_t['hour_of_day']
        dow = cur_t['day_of_week']
        month = cur_t['timestamp'].month
        
        hr_sin = np.sin(2 * np.pi * hr / 24.0)
        hr_cos = np.cos(2 * np.pi * hr / 24.0)
        dow_sin = np.sin(2 * np.pi * dow / 7.0)
        dow_cos = np.cos(2 * np.pi * dow / 7.0)
        month_sin = np.sin(2 * np.pi * month / 12.0)
        month_cos = np.cos(2 * np.pi * month / 12.0)
        
        feats = y_past + [
            y_roll_mean_6, y_roll_std_6, y_roll_mean_24, y_roll_std_24, y_min_24, y_max_24,
            temp, rh, vpd, dp_dep, surge, harm, is_harm,
            hr_sin, hr_cos, dow_sin, dow_cos, month_sin, month_cos
        ]
        future_targets = target[i+1 : i+1+HORIZONS]
        
        X_list.append(feats)
        Y_list.append(future_targets)

    X = np.array(X_list)
    Y = np.array(Y_list)

    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    Y_train, Y_val = Y[:split_idx], Y[split_idx:]

    print(f"Training Samples: {len(X_train)} | Out-of-Sample Holdout Samples: {len(X_val)}")

    base_lgb = LGBMRegressor(
        n_estimators=140,
        learning_rate=0.035,
        max_depth=6,
        num_leaves=31,
        subsample=0.85,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    multi_forecaster = MultiOutputRegressor(base_lgb, n_jobs=-1)
    multi_forecaster.fit(X_train, Y_train)

    val_preds = multi_forecaster.predict(X_val)

    horizon_sigmas = np.std(Y_val - val_preds, axis=0)
    horizon_maes = np.mean(np.abs(Y_val - val_preds), axis=0)
    horizon_r2s = [r2_score(Y_val[:, h], val_preds[:, h]) for h in range(HORIZONS)]

    print("-" * 60)
    print(f"Horizon +1h : R2 = {horizon_r2s[0]:.4f} | MAE = {horizon_maes[0]:.2f} ug/m3 | Uncertainty 90% sigma = +/-{horizon_sigmas[0]*1.645:.2f}")
    print(f"Horizon +3h : R2 = {horizon_r2s[2]:.4f} | MAE = {horizon_maes[2]:.2f} ug/m3 | Uncertainty 90% sigma = +/-{horizon_sigmas[2]*1.645:.2f}")
    print(f"Horizon +6h : R2 = {horizon_r2s[5]:.4f} | MAE = {horizon_maes[5]:.2f} ug/m3 | Uncertainty 90% sigma = +/-{horizon_sigmas[5]*1.645:.2f}")
    print(f"Horizon +12h: R2 = {horizon_r2s[11]:.4f} | MAE = {horizon_maes[11]:.2f} ug/m3 | Uncertainty 90% sigma = +/-{horizon_sigmas[11]*1.645:.2f}")
    print(f"Horizon +24h: R2 = {horizon_r2s[23]:.4f} | MAE = {horizon_maes[23]:.2f} ug/m3 | Uncertainty 90% sigma = +/-{horizon_sigmas[23]*1.645:.2f}")
    print("-" * 60)

    forecaster_obj = AirQuality24hForecaster(multi_forecaster, horizon_sigmas, LAGS)

    os.makedirs(os.path.join(project_dir, "models"), exist_ok=True)
    model_path = os.path.join(project_dir, "models", "air_quality_forecaster.joblib")
    joblib.dump(forecaster_obj, model_path, compress=3)
    print(f"Successfully saved 24-Hour Forecaster model to: {model_path}")
