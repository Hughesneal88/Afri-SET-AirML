import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("=== Training PMC12115728-Enhanced Primary Candidate Random Forest Model ===")
project_dir = os.path.dirname(os.path.abspath(__file__))

train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv")).dropna(subset=['pm25', 'PM25'])
holdout_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv")).dropna(subset=['pm25', 'PM25'])

def add_pmc_smoothing(df):
    X_df = df.copy()
    # Paper Innovation: 10-sample moving average pre-smoothing
    X_df['pm25_smoothed'] = X_df['pm25'].rolling(window=10, min_periods=1).mean()
    X_df['pm25_rh_interaction'] = X_df['pm25_smoothed'] * X_df['sample_rh']
    X_df['rolling_mean_pm25'] = X_df['pm25_smoothed'].rolling(window=3, min_periods=1).mean()
    return X_df

train_prep = add_pmc_smoothing(train_df)
holdout_prep = add_pmc_smoothing(holdout_df)

cols = [
    'pm25_smoothed', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
    'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
    'is_harmattan_month', 'harmattan_score', 'is_harmattan'
]

X_train = train_prep[cols]
y_train = train_prep['PM25'].values

X_holdout = holdout_prep[cols]
y_holdout = holdout_prep['PM25'].values

rf_best = RandomForestRegressor(
    n_estimators=300,
    max_depth=14,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_best.fit(X_train, y_train)

train_preds = rf_best.predict(X_train)
train_r2 = r2_score(y_train, train_preds)

holdout_preds = rf_best.predict(X_holdout)
holdout_r2 = r2_score(y_holdout, holdout_preds)
mae = mean_absolute_error(y_holdout, holdout_preds)
rmse = root_mean_squared_error(y_holdout, holdout_preds)
bias = np.mean(holdout_preds - y_holdout)

print(f"Train R² Score: {train_r2:.4f}")
print(f"=== PMC-Enhanced Primary RF (Unseen Holdout Generalization) ===")
print(f"Unseen Holdout R² Score: {holdout_r2:.4f}")
print(f"MAE: {mae:.2f} µg/m³")
print(f"RMSE: {rmse:.2f} µg/m³")
print(f"Systematic Bias: {bias:+.2f} µg/m³")

# Save as updated best model
model_path = os.path.join(project_dir, "models", "pmc_enhanced_best_rf.joblib")
joblib.dump(rf_best, model_path)
print(f"Saved PMC-Enhanced Best Model to: {model_path}")
