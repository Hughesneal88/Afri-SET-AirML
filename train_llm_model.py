import os
import pandas as pd
import numpy as np
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

print("--- Step 1: Loading Training Data ---")
project_dir = os.path.dirname(os.path.abspath(__file__))
train_path = os.path.join(project_dir, "web_data", "train_data.csv")
test_path = os.path.join(project_dir, "web_data", "out_of_sample_test.csv")

if not os.path.exists(train_path):
    print("Error: train_data.csv not found.")
    exit(1)

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

feature_cols = [
    'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
    'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
    'is_harmattan_month', 'harmattan_score', 'is_harmattan'
]

X_train = train_df[feature_cols].copy()
y_train = train_df['PM25'].values

X_test = test_df[feature_cols].copy()
y_test = test_df['PM25'].values

print(f"Train samples: {len(X_train)}, Holdout test samples: {len(X_test)}")

print("--- Step 2: Building and Training Deep Neural / LLM Calibration Model ---")
# Deep Architecture: (256, 128, 64) with Adam optimizer and early stopping
llm_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('mlp', MLPRegressor(
        hidden_layer_sizes=(256, 128, 64),
        activation='relu',
        solver='adam',
        alpha=0.001,
        learning_rate='adaptive',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=15
    ))
])

llm_pipeline.fit(X_train, y_train)

print("--- Step 3: Model Evaluation on Out-of-Sample Holdout ---")
y_pred = llm_pipeline.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)

print(f"Deep Neural LLM Model Holdout R²: {r2:.4f}")
print(f"Deep Neural LLM Model Holdout MAE: {mae:.2f} µg/m³")
print(f"Deep Neural LLM Model Holdout RMSE: {rmse:.2f} µg/m³")

print("--- Step 4: Exporting Joblib Model ---")
os.makedirs("models", exist_ok=True)
model_path = os.path.join(project_dir, "models", "llm_calibration_model.joblib")
joblib.dump(llm_pipeline, model_path)
print(f"Successfully saved LLM Calibration Model to: {model_path}")
