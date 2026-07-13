# Chapter 3: Methodology

This chapter details the experimental design, data sources, preprocessing pipelines, feature engineering formulations, machine learning model architectures, and validation frameworks developed to calibrate the low-cost QuantAQ Modulair-PM sensor against the reference-grade Teledyne API T640 monitor.

---

## 3.1 Experimental Co-location and Data Sources

### 3.1.1 Co-location Site and Environmental Context
The experimental data collection was conducted at the **African Clean Air Technology Centre (Afri-SET)**, situated within the Department of Physics at the University of Ghana, Legon, Accra ($5.651221^\circ\text{ N}, -0.185531^\circ\text{ W}$). Accra has a tropical savanna climate characterized by two distinct meteorological seasons:
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

To capture the physical and chemical behavior of the sensor and its environmental interferences, several domain-specific features were engineered.

### 3.3.1 Aerosol Hygroscopicity and Temperature Interaction
To model the hygroscopic growth of particles in high relative humidity, we engineered an interaction term between the raw sensor measurement and relative humidity:
$$\text{Interaction}_{\text{PM-RH}} = \text{pm25} \times \text{sample\_rh}$$
This interaction allows the model to scale its correction non-linearly when high relative humidity and high particulate loadings occur simultaneously.

### 3.3.2 Temporal and Diurnal Features
Air pollution concentrations and boundary layer heights follow strong diurnal and weekly cycles. These were captured using:
- **Hour of Day** ($H \in [0, 23]$): Represents the diurnal traffic, boundary layer height, and temperature variations.
- **Day of Week** ($D \in [0, 6]$): Captures anthropogenic activity differences between weekdays and weekends.

### 3.3.3 Rolling Temporal Statistics
To incorporate atmospheric continuity and local trends, short-term rolling statistics were calculated on the raw sensor measurements using a rolling window ($w = 3$ hours):
- **Rolling Mean**: Captures the short-term background trend:
  $$\text{rolling\_mean\_pm25}_t = \frac{1}{w} \sum_{i=0}^{w-1} \text{pm25}_{t-i}$$
- **Rolling Standard Deviation**: Captures short-term volatility and rapid changes in concentration:
  $$\text{rolling\_std\_pm25}_t = \sqrt{\frac{1}{w-1} \sum_{i=0}^{w-1} (\text{pm25}_{t-i} - \text{rolling\_mean\_pm25}_t)^2}$$
To avoid missing values at the beginning of the time-series, the first $w-1$ values were backfilled with the raw `pm25` value.

### 3.3.4 Harmattan and Dust Storm Indicators
To handle the unique dust loading during the dry winter months, three features were developed:
- `is_harmattan_month`: A binary flag ($1$ if the month is in November, December, January, February, or March; $0$ otherwise).
- `is_harmattan`: A localized seasonal indicator mapping active dust transport periods based on low humidity and high coarse-particle ratios.
- `harmattan_score`: A continuous variable estimating dust severity:
  $$\text{harmattan\_score} = \begin{cases} 
  f(\text{coarse\_ratio}, \text{RH}) & \text{if dry season months} \\
  0 & \text{otherwise}
  \end{cases}$$

### 3.3.5 Feature Scaling
For algorithms sensitive to scale (such as Neural Networks), continuous features were standardized to have zero mean and unit variance using the StandardScaler:
$$z = \frac{x - \mu}{\sigma}$$
where $\mu$ and $\sigma$ are the mean and standard deviation of the feature calculated *only* from the training partition to prevent data leakage.

---

## 3.4 Model Architectures and Training

Three modeling paradigms were implemented and compared:

### 3.4.1 Baseline Model: Linear Regression
A standard Multiple Linear Regression (MLR) model was implemented as a baseline:
$$\text{PM25}_{\text{reference}} = \beta_0 + \beta_1 \text{pm25}_{\text{raw}} + \beta_2 \text{sample\_temp} + \beta_3 \text{sample\_rh} + \beta_4 \text{Interaction}_{\text{PM-RH}} + \epsilon$$

### 3.4.2 Ensemble Model: Random Forest Regressor
The primary machine learning model is a **Random Forest Regressor**, which constructs an ensemble of decision trees using bootstrap aggregation (bagging) and random feature selection:
- **Structure**: Trained with 200 decision trees (`n_estimators=200`).
- **Hyperparameter Optimization**: Conducted using Grid Search (`GridSearchCV`) over a hyperparameter space:
  - `n_estimators`: $[200, 500]$
  - `max_depth`: $[10, 15, 20, \text{None}]$
  - `min_samples_split`: $[2, 5, 10]$
- **Objective Function**: Minimize the Mean Absolute Error (MAE) during training.

### 3.4.3 Deep Learning Model: Multi-Layer Perceptron (MLP) Regressor
To capture highly non-linear high-dimensional interactions, an artificial neural network was built using Scikit-Learn's `MLPRegressor`:
- **Architecture**: A feedforward neural network comprising:
  - Input layer mapping the engineered feature vector.
  - A hidden layer containing 128 neurons (`hidden_layer_sizes=(128,)`).
  - Output layer containing a single neuron with linear activation to output the calibrated $\text{PM}_{2.5}$ concentration.
- **Hyperparameters**:
  - Activation function: Hyperbolic tangent (`activation='tanh'`).
  - Optimization solver: Adam (`solver='adam'`).
  - Regularization parameter: L2 penalty parameter $\alpha = 0.01$ (`alpha=0.01`).
  - Batch size: 64 (`batch_size=64`).
  - Training control: Early stopping enabled (`early_stopping=True`) to prevent overfitting.

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
