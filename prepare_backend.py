import os
import glob
import pandas as pd
import numpy as np
import joblib

print("--- Step 1: Loading Hourly Data ---")
ref_path = "Teledyne_T640/2024-2026 T640.csv"
df_ref = pd.read_csv(ref_path)
df_ref['timestamp'] = pd.to_datetime(df_ref['Timestamp (UTC+0)'], errors='coerce', utc=True).dt.tz_localize(None)
df_ref = df_ref.dropna(subset=['timestamp', 'PM25']).sort_values('timestamp').set_index('timestamp')

mod_files_2024 = glob.glob("mod-PM068_2024/*.csv")
mod_files_2025 = glob.glob("mod-PM068_2025/*.csv")
all_mod_files = mod_files_2024 + mod_files_2025

sensor_hourly_list = []
for f in all_mod_files:
    try:
        df_temp = pd.read_csv(f, usecols=['timestamp', 'pm25', 'sample_temp', 'sample_rh', 'pm25_env'])
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'], errors='coerce', utc=True).dt.tz_localize(None)
        df_temp = df_temp.dropna(subset=['timestamp', 'pm25']).set_index('timestamp').resample('1h').mean().dropna()
        sensor_hourly_list.append(df_temp)
    except Exception:
        pass

sensor_hourly = pd.concat(sensor_hourly_list).sort_index()
sensor_hourly = sensor_hourly.groupby(sensor_hourly.index).mean()

merged_df = pd.merge(sensor_hourly, df_ref[['PM25']], left_index=True, right_index=True, how='inner')
merged_df = merged_df.dropna(subset=['pm25', 'PM25'])

print("--- Step 2: Atmospheric Physics & LLM Feature Engineering ---")
temp = merged_df['sample_temp']
rh = merged_df['sample_rh']
pm25 = merged_df['pm25']

merged_df['hour_of_day'] = merged_df.index.hour
merged_df['day_of_week'] = merged_df.index.dayofweek

merged_df['rolling_mean_pm25'] = merged_df['pm25'].rolling(window=3, min_periods=1).mean()
merged_df['rolling_std_pm25'] = merged_df['pm25'].rolling(window=3, min_periods=1).std().fillna(0)

merged_df['pm25_rh_interaction'] = pm25 * rh

# Novel Thermodynamic Atmospheric Features
# Saturation Vapor Pressure e_s(T) in kPa (Tetens Formula)
e_s = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
# Vapor Pressure Deficit (VPD)
merged_df['vapor_pressure_deficit'] = e_s * (1.0 - (rh / 100.0))
# Dew Point Depression
dew_point_temp = temp - ((100.0 - rh) / 5.0)
merged_df['dew_point_depression'] = temp - dew_point_temp
# Deliquescence Relative Humidity Exponential Surge (> 75% RH)
merged_df['rh_deliquescence_surge'] = np.where(rh > 75.0, np.exp((rh - 75.0) / 10.0), 0.0)

# Harmattan Flags
harmattan_months = {11, 12, 1, 2, 3}
merged_df['month'] = merged_df.index.month
merged_df['is_harmattan_month'] = merged_df['month'].isin(harmattan_months).astype(int)

window_hours = 24 * 30
merged_df['pm25_roll_mean'] = merged_df['pm25'].rolling(window=window_hours, min_periods=24).mean().fillna(pm25.mean())
merged_df['pm25_roll_std'] = merged_df['pm25'].rolling(window=window_hours, min_periods=24).std(ddof=0).replace(0, np.nan).fillna(pm25.std())
merged_df['pm25_z'] = (pm25 - merged_df['pm25_roll_mean']) / merged_df['pm25_roll_std']

merged_df['pm_spike'] = (merged_df['pm25_z'] > 1.5).astype(int)
merged_df['low_rh'] = (rh < 30).astype(int)

merged_df['harmattan_score'] = merged_df[['is_harmattan_month', 'pm_spike', 'low_rh']].fillna(0).sum(axis=1)
merged_df['is_harmattan'] = ((merged_df['is_harmattan_month'] == 1) & ((merged_df['pm_spike'] == 1) | (merged_df['low_rh'] == 1))).astype(int)

merged_df = merged_df.drop(columns=['month', 'pm25_roll_mean', 'pm25_roll_std', 'pm25_z', 'pm_spike', 'low_rh'])

print("--- Step 3: Exporting Partition Datasets ---")
os.makedirs("web_data", exist_ok=True)

n_total = len(merged_df)
train_end = int(n_total * 0.60)
test_end = int(n_total * 0.75)

train_df = merged_df.iloc[:train_end]
test_df = merged_df.iloc[train_end:test_end]
holdout_df = merged_df.iloc[test_end:]

print(f"Full Dataset: {len(merged_df)} records")
print(f"Train Dataset: {len(train_df)} records")
print(f"Test Dataset: {len(test_df)} records")
print(f"Holdout Dataset: {len(holdout_df)} records")

merged_df.reset_index().to_csv("web_data/full_dataset.csv", index=False)
train_df.reset_index().to_csv("web_data/train_data.csv", index=False)
test_df.reset_index().to_csv("web_data/test_data.csv", index=False)
holdout_df.reset_index().to_csv("web_data/out_of_sample_test.csv", index=False)

print("Successfully exported all partition datasets with novel thermodynamic features!")
