# Chapter 3: Methodology

This chapter details the experimental design, data sources, preprocessing pipelines, feature engineering formulations, machine learning model architectures, and validation frameworks developed to calibrate the low-cost QuantAQ Modulair-PM sensor against the reference-grade Teledyne API T640 monitor.

---

## 3.1 Experimental Co-location and Data Sources

### 3.1.1 Co-location Site and Environmental Context
The experimental data collection was conducted at the **African Sensor Evaluation and Training Facility (Afri-SET)**, situated within the Department of Physics at the University of Ghana, Legon, Accra ($5.651221^\circ\text{ N}, -0.185531^\circ\text{ W}$). Accra has a tropical savanna climate characterized by two distinct meteorological seasons:
1. **The Wet Season (April to October)**: Influenced by the West African Monsoon, bringing frequent, heavy precipitation and high ambient relative humidity (often exceeding 80–90%).
2. **The Dry Harmattan Season (November to March)**: Influenced by dry northeasterly trade winds blowing from the Sahara Desert. This season is characterized by heavy loading of coarse mineral dust, extremely low relative humidity ($<30\%$), and elevated ambient particulate concentrations.

### 3.1.2 Low-Cost Sensor Unit: QuantAQ Modulair-PM
The low-cost sensor evaluated in this study is the **QuantAQ Modulair-PM** (specifically unit `MOD-PM-01068`). This device is an integrated air quality monitor containing:
- **Alphasense OPC-N3 Optical Particle Counter**: Measures particle counts across 24 size bins spanning $0.35\ \mu\text{m}$ to $40\ \mu\text{m}$. It outputs raw particle counts, calculated PM mass concentrations (`pm1`, `pm25`, `pm10`), and diagnostic parameters (`opcn3_temp`, `opcn3_rh`).
- **Meteorological Sensors**: Measures ambient temperature (`sample_temp` in $^\circ\text{C}$), relative humidity (`sample_rh` as a percentage), and barometric pressure (`sample_pres` in $\text{hPa}$).
- **QuantAQ Calibration Algorithm**: Outputs proprietary corrected PM values (`pm25_env`, `pm10_env`). In this study, we utilize the raw sensor reading (`pm25`) as our primary feature to build independent, localized calibration models.

### 3.1.3 Reference Monitor: Teledyne API T640
The ground truth reference data was collected using a co-located **Teledyne API T640** particulate monitor. The T640 utilizes broad-spectrum LED light-scattering spectroscopy to provide continuous, high-resolution hourly measurements of $\text{PM}_{2.5}$ mass concentrations. It is a US EPA Federal Equivalent Method (FEM) instrument with an operating range of $0$ to $10,000\ \mu\text{g/m}^3$ and a measurement resolution of $<0.1\ \mu\text{g/m}^3$. 

---

## 3.2 Data Preprocessing and Alignment

### 3.2.1 Temporal Alignment and Reindexing
The low-cost sensor collects data at a high temporal resolution (typically 1-minute intervals), whereas the Teledyne T640 reference monitor logs hourly averages. To align the datasets:
1. The 1-minute Modulair-PM sensor data was aggregated to hourly averages using the mean.
2. Both datasets were converted to Coordinated Universal Time (UTC) and aligned by index.
3. Due to potential offsets and minor gaps, the sensor data was reindexed to match the reference database index (`Timestamp (UTC+0)`), ensuring complete temporal alignment.

### 3.2.2 Quality Control and Outlier Handling
To ensure data integrity, data quality filters were applied:
- **Negative Values**: Reference $\text{PM}_{2.5}$ measurements below $0\ \mu\text{g/m}^3$ (due to instrument zero-drift) were flagged and removed.
- **Instrument Malfunction Flags**: Data points where the Modulair-PM sensor flagged device status errors (`flag != 0`) were excluded.
- **Missing Data**: Gaps of $\le 2$ consecutive hours in the low-cost sensor data were filled using linear interpolation. Gaps exceeding 2 hours were dropped from the training and testing sets to prevent introducing artificial signals.
- **Outlier Detection**: The Interquartile Range (IQR) method was applied to raw particulate measurements. Extreme spikes exceeding $Q3 + 3 \times \text{IQR}$ were cross-checked with reference measurements; if the reference monitor did not register a corresponding spike, the sensor data was treated as an instrumental error and removed. Genuine high-pollution events (such as dust storms) where both instruments spiked were preserved.

---

## 3.3 Feature Engineering

To capture the physical and chemical behavior of optical particle counters, environmental humidity interference, and temporal dynamics, a comprehensive 75-feature vector was engineered.

### 3.3.1 Aerosol Hygroscopicity and Kohler Growth Physics
Optical particle counters overestimate particulate mass at high relative humidity ($\text{RH}$) due to water uptake (hygroscopic swelling). To explicitly model this non-linear growth without forcing tree algorithms to memorize noise:
1. **Multi-Gamma Kohler Growth Curves**: Eight distinct empirical growth curves were derived across exponents $\gamma \in \{0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50\}$:
   $$f(\text{RH}, \gamma) = \text{pm25} \times \left(1 - \frac{\text{RH}}{100}\right)^{-\gamma}$$
2. **Droplet Swelling Ratio & Scaled Growth**:
   $$\text{rh\_growth\_ratio} = \frac{\text{RH} / 100}{1 - (\text{RH} / 100) + 10^{-4}}, \quad \text{pm25\_kohler\_scaled} = \frac{\text{pm25}}{1 + 0.15 \times \text{rh\_growth\_ratio}}$$
3. **Exponential Deliquescence Surge**: Captures extreme condensation when relative humidity exceeds $75\%$:
   $$\text{rh\_deliquescence\_surge} = \begin{cases} \exp\left(\frac{\text{RH} - 75}{10}\right) & \text{if } \text{RH} > 75\% \\ 0 & \text{otherwise} \end{cases}$$

### 3.3.2 Thermodynamics (Vapor Pressure Deficit, Absolute Humidity, and Dew Point)
To capture atmospheric water mass density and evaporation pressure:
1. **Saturation Vapor Pressure ($e_s$)**: Computed using Tetens formula ($e_s$ in kPa, $T$ in $^\circ\text{C}$):
   $$e_s(T) = 0.61078 \times \exp\left(\frac{17.27 \times T}{T + 237.3}\right)$$
2. **Vapor Pressure Deficit (VPD)**: Quantifies atmospheric drying capacity:
   $$\text{VPD} = e_s(T) \times \left(1 - \frac{\text{RH}}{100}\right)$$
3. **Absolute Humidity ($AH$)**: Exact water mass density in ambient air ($\text{g/m}^3$):
   $$AH = \frac{216.7 \times e_s(T) \times (\text{RH} / 100)}{T + 273.15}$$
4. **Dew Point Temperature ($T_{\text{dew}}$)**: Computed via Magnus equation:
   $$\gamma(T, \text{RH}) = \frac{17.27 \times T}{237.3 + T} + \ln\left(\frac{\text{RH}}{100}\right), \quad T_{\text{dew}} = \frac{237.3 \times \gamma(T, \text{RH})}{17.27 - \gamma(T, \text{RH})}$$
   $$\text{dew\_point\_dep} = T - T_{\text{dew}}$$

### 3.3.3 Multi-Window EWMA and Rolling Trend Features
To model local atmospheric continuity and rapid air quality spikes (e.g. traffic or biomass plumes):
- **Exponentially Weighted Moving Averages (EWMA)**: Calculated across 9 time spans ($w \in \{1, 2, 3, 4, 6, 8, 12, 16, 24\}$ hours):
  $$\text{EWMA}_t(w) = \alpha \cdot \text{pm25}_t + (1 - \alpha) \cdot \text{EWMA}_{t-1}(w), \quad \alpha = \frac{2}{w + 1}$$
- **Rolling Means, Standard Deviations, and Differences**: Computed across the same 9 windows ($w \in \{1, 2, 3, 4, 6, 8, 12, 16, 24\}$) to capture short-term background levels and volatility ($\text{pm25} - \text{rolling\_mean}_w$).

### 3.3.4 Cyclical Temporal Harmonic Encodings
To avoid artificial boundary discontinuities at midnight ($23 \to 0$) or year-end ($12 \to 1$), temporal dimensions were mapped onto continuous 2D circular harmonics:
- **Diurnal Cycles**: $\sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \, \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$
- **Weekly Cycles**: $\sin\left(\frac{2\pi \cdot \text{day}}{7}\right), \, \cos\left(\frac{2\pi \cdot \text{day}}{7}\right)$
- **Annual Seasonal Cycles**: $\sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \, \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$

### 3.3.5 Harmattan and Dust Storm Indicators
To handle regional mineral dust transport during the dry season (November to March), localized dust storm indicators (`is_harmattan_month`, `harmattan_score`, `is_harmattan`) were computed based on coarse-particle ratios and low relative humidity.

---

## 3.4 Model Architectures and Training

Four modeling paradigms were implemented and evaluated:

### 3.4.1 Baseline Model: Linear Regression
A standard Multiple Linear Regression (MLR) model was implemented as a baseline:
$$\text{PM25}_{\text{reference}} = \beta_0 + \beta_1 \text{pm25}_{\text{raw}} + \beta_2 \text{sample\_temp} + \beta_3 \text{sample\_rh} + \beta_4 \text{Interaction}_{\text{PM-RH}} + \epsilon$$

### 3.4.2 Ensemble Model: Random Forest Regressor
A **Random Forest Regressor** constructing an ensemble of decision trees using bagging and random feature selection:
- **Structure**: Trained with 200 decision trees (`n_estimators=200`).
- **Hyperparameter Optimization**: Conducted using Grid Search (`GridSearchCV`).

### 3.4.3 Deep Learning Model: Multi-Layer Perceptron (MLP) Regressor
A feedforward artificial neural network trained using Scikit-Learn's `MLPRegressor`:
- **Architecture**: Single hidden layer with 128 neurons (`hidden_layer_sizes=(128,)`), hyperbolic tangent activation (`tanh`), Adam solver, and L2 regularization ($\alpha = 0.01$).

### 3.4.4 Primary Architecture: Stacked Physics-Informed Meta-Ensemble (SPIME v4)
To maximize accuracy while completely eliminating generalization overfitting, a two-level stacked meta-ensemble was developed (`train_stacked_physics_ensemble.py`):

1. **Level 0 Base Estimators**:
   - **Regularized Random Forest**: 600 decision trees (`max_depth=32`, `min_samples_split=2`, `max_features=0.55`).
   - **Regularized ExtraTrees**: 600 extremely randomized trees (`max_depth=34`, `min_samples_split=2`, `max_features=0.55`).
   - **LightGBM Regressor**: 1,500 leaf-wise gradient boosted trees (`learning_rate=0.015`, `max_depth=18`, `num_leaves=380`, `reg_alpha=0.005`, `reg_lambda=0.05`).
   - **HistGradientBoosting Regressor**: 1,200 histogram binned gradient iterations (`learning_rate=0.015`, `max_depth=24`, `min_samples_leaf=2`).
2. **Level 1 Out-of-Fold (OOF) Stacking Matrix**:
   - To prevent meta-learner data leakage, a **5-Fold Cross-Validation** strategy was applied to generate out-of-fold prediction matrix $S_{\text{train}}$. Base models only predict on held-out samples they never saw during training folds.
3. **Level 2 Meta-Learner**:
   - An $L_2$-regularized `RidgeCV` model combines out-of-fold predictions from the four base estimators to generate the final reference-grade $\text{PM}_{2.5}$ output ($\mu\text{g/m}^3$).

---

## 3.5 Model Validation and Testing Strategy

To evaluate how well the models generalize to unseen future data and prevent temporal data leakage:
1. **Chronological Train-Test Split**: The co-located dataset was split chronologically rather than randomly. A training partition (75% or 80%) consisting of earlier records (primarily 2024 data) was used to train the models, while a holdout test partition (20% to 25%) consisting of subsequent records (2025 data) was used to evaluate generalization.
2. **Time-Series Cross-Validation**: A 5-fold Time Series Split (`TimeSeriesSplit`) was applied during hyperparameter optimization, where the training set in each fold grows sequentially, and the validation set is always chronologically subsequent to the training set. This simulates a real-world deployment scenario where models calibrated on past data must predict future air quality.

---

## 3.6 Evaluation Framework

Model performance is assessed quantitatively using three primary metrics:

1. **Coefficient of Determination ($R^2$ Score)**: Measures the proportion of variance in the reference data explained by the calibration model:
   $$R^2 = 1 - \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{\sum_{i=1}^n (y_i - \bar{y})^2}$$
2. **Mean Absolute Error (MAE)**: Measures the average magnitude of absolute errors (expressed in $\mu\text{g/m}^3$):
   $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$
3. **Root Mean Squared Error (RMSE)**: Penalizes larger deviations, making it sensitive to extreme prediction errors:
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$

In these equations, $y_i$ is the actual reference $\text{PM}_{2.5}$ value from the Teledyne T640, $\hat{y}_i$ is the calibrated value predicted by the model, $\bar{y}$ is the mean of the actual reference values, and $n$ is the total number of test samples.

In addition to quantitative metrics, **Residual Diagnostics** were conducted:
- **Residual Distribution Plotting**: Histograms and Kernel Density Estimation (KDE) to verify if prediction errors are normally distributed.
- **Quantile-Quantile (Q-Q) Plots**: Standardized residuals plotted against theoretical normal quantiles to assess deviations from normality.
- **Heteroscedasticity Analysis**: Scatter plots of residuals versus predicted values to determine if the error variance is constant across the range of predictions.
- **Feature Importance Analysis**: Extraction of tree-based feature importances from the Random Forest model to identify the physical parameters most critical to correcting sensor readings.
