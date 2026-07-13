# Copilot Instructions for Modulair-PM

## Project Overview

This project develops machine learning-based calibration models to improve PM2.5 (Particulate Matter ≤ 2.5 micrometers) prediction accuracy from low-cost air quality sensors by correcting systematic biases using reference-grade measurements and environmental factors.

**Success Criteria**: R² ≥ 0.85, MAE ≤ 5 µg/m³

## Build, Test & Validation

### Python Environment
- **Python Version**: 3.13
- **Primary Libraries**: scikit-learn, numpy, scipy, pandas, matplotlib, joblib
- **Installation**: Create virtual environment and install dependencies from imports in `Notebook.ipynb`

### Model Training & Validation
- **Primary Notebook**: `Notebook.ipynb` - Contains the full ML pipeline (data preprocessing, feature engineering, model training, evaluation)
- **Models Stored**: `.joblib` format in repository root (e.g., `random_forest_pm25_model.joblib`, `random_forest_pm25_model_update.joblib`)
- **Training Split**: 80/20 train-test with temporal stratification:
  - Training: 2024 data
  - Validation: Early 2025 data
  - Testing: Latest 2025 data
- **Cross-Validation**: 5-fold Time Series CV to prevent temporal leakage

### Evaluation Metrics
Primary metrics computed on test set:
- **R² Score**: Variance explained (target ≥ 0.85)
- **MAE**: Mean Absolute Error in µg/m³ (target ≤ 5)
- **RMSE**: Root Mean Square Error (penalizes large errors)

Secondary metrics:
- **MAPE**: Mean Absolute Percentage Error
- **Bias**: Mean prediction error (should be near zero)
- **Correlation**: Pearson correlation between predicted and actual

## Architecture & Data Flow

### Data Sources
| Source | Description | Time Period | Variables |
|--------|---|---|---|
| **Modular PM Sensors** | Low-cost sensor units (mod-PM068) | 2024-2025 | Raw PM2.5, Temperature, RH |
| **Reference Equipment** | Teledyne T640 (EPA-equivalent) | 2024-2025 | Ground truth PM2.5 |
| **Meteorological Data** | Ambient conditions | 2024-2025 | Precipitation, wind patterns |

### Feature Engineering Pipeline
**Primary Features**:
- `pm25`: Raw sensor PM2.5 (log-transformed for right-skewed distribution)
- `sample_temp`: Ambient temperature (normalized)
- `sample_rh`: Relative humidity (normalized)

**Temporal Features**:
- `hour_of_day` (0-23): Diurnal pollution patterns (traffic peaks, boundary layer)
- `day_of_week` (0-6): Weekday vs. weekend anthropogenic behavior
- `month_of_year` (1-12): Seasonal PM2.5 variations
- `season_indicator`: Categorical (Dry/Wet season)

**Derived Features** (computed with 24-hour rolling window):
- `rolling_mean_pm25`: Smoothed trend, reduces noise
- `rolling_std_pm25`: Volatility indicator, captures rapid concentration changes
- `pm25_rh_interaction`: `pm25 × RH` (hygroscopic particle growth)
- `pm25_temp_interaction`: `pm25 × Temp` (temperature-dependent volatilization)

**Domain-Specific Features** (West African context):
- `is_harmattan_month`: Binary flag for dry season months (Nov-Mar)
- `harmattan_score`: Magnitude estimation for harmattan wind influence
- `is_harmattan`: Composite harmattan indicator

**Normalization**: StandardScaler (zero mean, unit variance) applied to all continuous features

### Model Candidates

#### Random Forest (Primary Model)
- **Architecture**: Ensemble of 100+ decision trees
- **Hyperparameters**: 
  - `max_depth`: 15-20 (prevents overfitting)
  - `min_samples_split`: 5-10
  - `min_samples_leaf`: 2-5
  - `max_features`: 'sqrt' (reduces tree correlation)
- **Advantages**: Non-linear relationships, robust to outliers, provides feature importance
- **Performance**: R² ~0.90, MAE ~1.90, RMSE ~4.34

#### MLP Neural Network
- **Architecture**: 3-layer network
  - Input: All engineered features
  - Hidden: 64-128 neurons with ReLU activation (tanh also tested)
  - Output: Linear activation for regression
- **Hyperparameters** (from grid search):
  - `solver`: 'adam' (default is 'lbfgs', adam better for large datasets)
  - `batch_size`: 64
  - `alpha`: 0.01 (L2 regularization)
  - `activation`: 'tanh'
  - `max_iter`: 1000
  - `early_stopping`: True
- **Use case**: Captures complex feature interactions; good for temporal dependencies

#### Baseline Model (Linear Regression)
- **Purpose**: Benchmark for comparison
- **Performance**: R² ~0.56, MAE ~6.22, RMSE ~8.92

## Key Conventions & Patterns

### Data Quality & Preprocessing
- **Missing Data**: Interpolate gaps ≤2 hours; use linear regression from temperature/RH for longer gaps
- **Outliers**: IQR-based detection
  - Extreme spikes (>200% normal range): Mark as instrumental error, impute
  - Legitimate high values (dust events, pollution): Retain
- **Data Stratification**: Daily, weekly, monthly aggregations for quality verification

### Hyperparameter Optimization
- **Method**: GridSearchCV with 5-fold time series cross-validation
- **Grid Space** (Random Forest):
  - `n_estimators`: [50, 100, 200, 300]
  - `max_depth`: [10, 15, 20, None]
  - `min_samples_split`: [2, 5, 10]
- **Optimization Metric**: MAE (directly interpretable in µg/m³)

### Model Persistence & Versioning
- **Format**: Joblib (.joblib)
- **Naming Convention**: Include iteration info (e.g., `random_forest_pm25_model_update2.joblib`)
- **Metadata**: Track training date, R² score, MAE, hyperparameters, feature list

### Real-Time Inference Pipeline
1. Read sensor data (raw PM2.5, Temp, RH)
2. Engineer features (rolling stats, interactions, temporal features)
3. Normalize features using training set statistics
4. Execute model prediction
5. Output corrected PM2.5 value
- **Latency Target**: <100ms for hourly data

### Error Analysis Patterns
- Examine residuals (predicted - actual) across conditions:
  - High vs. low pollution scenarios
  - Dry vs. wet seasons
  - Different times of day
- Identify systematic biases (model consistently over/under-predicts in specific conditions)
- Validate using feature importance (tree-based) to ensure model decisions are reasonable

### Retraining & Monitoring
- **Trigger**: Performance degradation >10% in MAE or when new data exceeds 500 samples
- **Schedule**: Quarterly or on-demand based on drift detection
- **Data Drift**: Monitor for concept drift (new pollution sources, seasonal shifts)

## Dataset Characteristics
- **Temporal Resolution**: Hourly measurements
- **Sample Size**: 8,000+ data points per station
- **Data Period**: 12+ months (captures seasonal variations)
- **Seasonal Context**: West African Harmattan winds (Nov-Mar) significantly affect PM2.5

## Limitations & Considerations
- **Geographic Specificity**: Models trained at one location may not generalize to others; test transfer learning if needed
- **Sensor Drift**: Calibration becomes obsolete over time; implement time-stratified validation
- **Missing Environmental Variables**: Unmeasured factors (wind speed/direction, pollution source profiles) affect predictions
- **Extreme Events**: Limited data on extreme events (dust storms, fires); may need synthetic augmentation
