# LIST OF FIGURES

- **Figure 1.1:** Afri-SET Co-location Facility and Ambient Monitoring Platform at the Department of Physics, University of Ghana, Legon.
- **Figure 2.1:** Working Principle of Optical Particle Counters (OPC) based on Mie Light Scattering Theory.
- **Figure 2.2:** Aerosol Hygroscopic Particle Growth and Deliquescence Threshold Curve under Elevated Relative Humidity.
- **Figure 2.3:** Seasonal Meteorological Dynamics in West Africa: Monsoon Wet Season vs. Dry Saharan Harmattan Dust Transport.
- **Figure 3.1:** Geographic Co-location Site at Afri-SET, University of Ghana, Legon (5.6512° N, -0.1855° W).
- **Figure 3.2:** End-to-End Machine Learning Calibration Pipeline Architecture for Low-Cost Modulair-PM Sensors.
- **Figure 3.3:** Scatter Plot of Raw Modulair-PM PM₂.₅ Concentrations vs. Reference Teledyne API T640 Measurements across Calendar Months.
- **Figure 3.4:** Hourly Time-Series Comparison of Raw Low-Cost Sensor PM₂.₅ and Reference Teledyne T640 Data.
- **Figure 3.5:** Multi-Gamma Köhler Hygroscopic Growth Curves f(RH, γ) across Exponents γ ∈ [0.05, 0.50].
- **Figure 3.6:** Stacked Physics-Informed Meta-Ensemble (SPIME v4) Architecture showing Level 0 Base Learners and Level 1 RidgeCV Meta-Learner with 5-Fold OOF Stacking.
- **Figure 3.7:** Chronological Train-Test and Unseen 6-Month Out-of-Sample Holdout Validation Partition Scheme.
- **Figure 4.1:** Scatter Plot of Actual Teledyne T640 Reference PM₂.₅ vs. SPIME v4 Calibrated PM₂.₅ Predictions on 6-Month Unseen Holdout Data.
- **Figure 4.2:** Time-Series Tracking of Calibrated PM₂.₅ Predictions against Ground Truth Reference Measurements (Subset).
- **Figure 4.3:** Comparative Time-Series Prediction Performance: Multi-Layer Perceptron (MLP) Neural Network vs. Random Forest vs. SPIME v4 Meta-Ensemble.
- **Figure 4.4:** Top 20 Feature Importance Rankings Extracted from SPIME v4 Base Estimators highlighting Köhler Physics and Thermodynamic Predictors.
- **Figure 4.5:** Residual Error Histogram and Kernel Density Estimation (KDE) Distribution for the Calibrated SPIME v4 Model.
- **Figure 4.6:** Quantile-Quantile (Q-Q) Plot of Standardized Calibration Residuals against Theoretical Normal Quantiles.
- **Figure 4.7:** Homoscedasticity Diagnostic Plot: Calibration Model Residuals vs. Predicted PM₂.₅ Concentrations.

---

# LIST OF TABLES

- **Table 1.1:** Comparison of Reference-Grade Regulatory Particulate Monitors and Low-Cost Optical Particle Counters.
- **Table 2.1:** Summary of Literature on Machine Learning Calibration Algorithms for Low-Cost Air Quality Sensors (2017–2025).
- **Table 3.1:** Technical Specifications and Measurement Parameters of the QuantAQ Modulair-PM (Unit MOD-PM-01068).
- **Table 3.2:** Technical Specifications and Operating Parameters of the Teledyne API T640 Reference Monitor.
- **Table 3.3:** Systematic Summary of the 75 Engineered Physics-Informed, Thermodynamic, and Cyclical Temporal Features.
- **Table 3.4:** Optimal Hyperparameter Configurations for SPIME v4 Level 0 Base Estimators and Level 1 Meta-Learner.
- **Table 4.1:** Comparative Performance Metrics on Out-of-Sample Holdout Data (3,468 Unseen Hourly Samples across 6 Models).
- **Table 4.2:** Seasonal Performance Breakdown: Model Calibration Accuracy during Monsoon Wet Season vs. Harmattan Dry Season.
- **Table 4.3:** Generalization and Overfitting Gap Diagnostics (R²_train - R²_test) across Linear, Neural, and Meta-Ensemble Paradigms.

---

# LIST OF ABBREVIATIONS

| Abbreviation | Full Meaning / Description |
| :--- | :--- |
| **Afri-SET** | African Sensor Evaluation and Training Facility |
| **AH** | Absolute Humidity (g/m³) |
| **AI** | Artificial Intelligence |
| **ANN** | Artificial Neural Network |
| **API** | Advanced Pollution Instrumentation / Application Programming Interface |
| **BAM** | Beta Attenuation Monitor |
| **CO** | Carbon Monoxide |
| **COPD** | Chronic Obstructive Pulmonary Disease |
| **CV** | Cross-Validation |
| **DRH** | Deliquescence Relative Humidity |
| **EPA** | Environmental Protection Agency (United States) |
| **ET** | ExtraTrees (Extremely Randomized Trees) |
| **EWMA** | Exponentially Weighted Moving Average |
| **FEM** | Federal Equivalent Method (US EPA) |
| **FRM** | Federal Reference Method (US EPA) |
| **GBDT** | Gradient Boosted Decision Trees |
| **HistGB** | Histogram-Based Gradient Boosting Regressor |
| **IQR** | Interquartile Range |
| **KDE** | Kernel Density Estimation |
| **LCS** | Low-Cost Sensor(s) |
| **LED** | Light Emitting Diode |
| **LightGBM** | Light Gradient Boosting Machine |
| **LLM** | Large Language Model / Deep Neural LLM Regressor |
| **MAE** | Mean Absolute Error (µg/m³) |
| **ML** | Machine Learning |
| **MLP** | Multi-Layer Perceptron |
| **MLR** | Multiple Linear Regression |
| **MOD-PM** | Modulair Particulate Matter Sensor Unit |
| **MSE** | Mean Squared Error |
| **NO₂** | Nitrogen Dioxide |
| **NOₓ** | Nitrogen Oxides |
| **O₃** | Ozone |
| **OOF** | Out-of-Fold |
| **OPC** | Optical Particle Counter |
| **PM** | Particulate Matter |
| **PM₁** | Particulate Matter with aerodynamic diameter ≤ 1.0 µm |
| **PM₂.₅** | Particulate Matter with aerodynamic diameter ≤ 2.5 µm |
| **PM₁₀** | Particulate Matter with aerodynamic diameter ≤ 10 µm |
| **Q-Q** | Quantile-Quantile |
| **Q1 / Q3** | First Quartile (25th percentile) / Third Quartile (75th percentile) |
| **R²** | Coefficient of Determination |
| **RF** | Random Forest |
| **RH** | Relative Humidity (%) |
| **RidgeCV** | Ridge Regression with Built-in Cross-Validation |
| **RMSE** | Root Mean Squared Error (µg/m³) |
| **SLR** | Simple Linear Regression |
| **SPIME** | Stacked Physics-Informed Meta-Ensemble |
| **SSA** | Sub-Saharan Africa |
| **T_dew** | Dew Point Temperature (°C) |
| **UTC** | Coordinated Universal Time |
| **VPD** | Vapor Pressure Deficit (kPa) |
| **WHO** | World Health Organization |
| **XGBoost** | Extreme Gradient Boosting |
