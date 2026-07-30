import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.mixture import GaussianMixture
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

class AtmosphericMoE:
    """
    Mixture of Experts (MoE) classifier-gated ensemble specializing in 
    Harmattan Dust vs. Coastal Monsoon Relative Humidity regimes.
    """
    def __init__(self, n_experts=3):
        self.n_experts = n_experts
        self.gating = GaussianMixture(n_components=n_experts, random_state=42)
        self.experts = [RandomForestRegressor(n_estimators=100, max_depth=14, random_state=42, n_jobs=-1) for _ in range(n_experts)]
        self.n_features_in_ = 14

    def fit(self, X, y, regime_features):
        self.gating.fit(regime_features)
        regime_labels = self.gating.predict(regime_features)
        
        for k in range(self.n_experts):
            mask = (regime_labels == k)
            if np.sum(mask) > 50:
                self.experts[k].fit(X[mask], y[mask])
            else:
                self.experts[k].fit(X, y)

    def predict(self, X):
        # Extract regime features (sample_rh, sample_temp, is_harmattan)
        if isinstance(X, pd.DataFrame):
            regime_features = X[['sample_rh', 'sample_temp', 'is_harmattan']].values
            X_val = X.values
        else:
            regime_features = X[:, [2, 1, 10]]
            X_val = X

        probs = self.gating.predict_proba(regime_features)
        preds = np.column_stack([expert.predict(X_val) for expert in self.experts])
        
        # Soft Probability Weighted Blend
        final_pred = np.sum(probs * preds, axis=1)
        return final_pred

if __name__ == '__main__':
    print("--- Step 1: Training Atmospheric Mixture of Experts (MoE) Model ---")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    train_df = pd.read_csv(os.path.join(project_dir, "web_data", "train_data.csv"))
    test_df = pd.read_csv(os.path.join(project_dir, "web_data", "out_of_sample_test.csv"))

    cols = [
        'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
        'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
        'vapor_pressure_deficit', 'dew_point_depression', 'rh_deliquescence_surge',
        'is_harmattan_month', 'harmattan_score', 'is_harmattan'
    ]

    X_train = train_df[cols]
    y_train = train_df['PM25'].values

    X_test = test_df[cols]
    y_test = test_df['PM25'].values

    regime_train = train_df[['sample_rh', 'sample_temp', 'is_harmattan']].values

    moe = AtmosphericMoE(n_experts=3)
    moe.fit(X_train, y_train, regime_train)

    y_pred = moe.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)

    print(f"Atmospheric MoE Model Holdout R²: {r2:.4f}")
    print(f"Atmospheric MoE Model Holdout MAE: {mae:.2f} µg/m³")
    print(f"Atmospheric MoE Model Holdout RMSE: {rmse:.2f} µg/m³")

    os.makedirs("models", exist_ok=True)
    model_path = os.path.join(project_dir, "models", "moe_expert_model.joblib")
    joblib.dump(moe, model_path)
    print(f"Saved Atmospheric MoE Expert Model to: {model_path}")
