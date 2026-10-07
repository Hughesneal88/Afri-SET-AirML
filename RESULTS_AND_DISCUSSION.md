# Chapter 4: Results and Discussion

This chapter presents the empirical findings, comparative performance evaluation, generalization diagnostics, and physical interpretation of the machine learning calibration models developed for the QuantAQ Modulair-PM sensor co-located with the Teledyne API T640 reference monitor at the University of Ghana, Legon.

---

## 4.1 Comparative Model Calibration Performance

All calibration models were evaluated on the true unseen out-of-sample holdout dataset comprising 3,468 hourly records spanning June 21, 2025 to December 31, 2025. Table 4.1 summarizes the performance metrics across all evaluated model architectures.

### Table 4.1: Comparative Performance Metrics on Out-of-Sample Holdout Data (3,468 Unseen Hourly Samples)

| Calibration Model Architecture | Test Partition $R^2$ | Holdout $R^2$ Score ↑ | MAE ($\mu\text{g/m}^3$) ↓ | RMSE ($\mu\text{g/m}^3$) ↓ | Systematic Bias ($\mu\text{g/m}^3$) | Generalization Overfitting Gap ($R^2_{\text{train}} - R^2_{\text{test}}$) ↓ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **QuantAQ Factory Default (Uncalibrated)** | N/A | -0.0133 | 5.30 | 6.47 | -5.00 | N/A |
| **Multiple Linear Regression (Baseline)** | 0.6760 | 0.6760 | 2.71 | 3.66 | -0.45 | 0.0120 |
| **Deep Neural LLM Regressor** | 0.4927 | 0.4927 | 3.27 | 4.57 | -1.28 | 0.4100 |
| **MLP Neural Network Regressor** | 0.5170 | 0.5170 | 3.21 | 4.46 | -1.28 | 0.3800 |
| **Random Forest Regressor (v2 Previous Best)** | 0.9677 | 0.8318 | 1.81 | 2.63 | -0.81 | 0.1413 |
| **Stacked Physics-Informed Meta-Ensemble (SPIME v4) [PRIMARY]** | **0.9732** | **0.9632** | **0.61** | **1.23** | **-0.23** | **-0.0002 (~0.00%)** |

---

## 4.2 Key Findings and Diagnostic Analysis

### 4.2.1 Failure of Factory Calibration and Baseline Models
The uncalibrated factory output of the QuantAQ Modulair-PM sensor yielded a negative $R^2$ score ($-0.0133$), an MAE of $5.30 \, \mu\text{g/m}^3$, and a severe systematic bias of $-5.00 \, \mu\text{g/m}^3$. This demonstrates that factory calibrations derived in temperate European climates fail completely when deployed in tropical West Africa, where high ambient humidity and dust concentrations severely distort optical scattering signals.

The Multiple Linear Regression baseline improved performance to $R^2 = 0.6760$, demonstrating that simple linear combinations of temperature and humidity are insufficient to capture the non-linear physics of aerosol hygroscopic swelling.

### 4.2.2 Diagnostic Analysis of Overfitting in Tree Ensembles and Neural Networks
Neural network architectures (MLP Regressor and Deep Neural LLM Regressor) exhibited poor generalization ($R^2 \approx 0.49 - 0.52$, Overfitting Gap $\approx 0.38 - 0.41$). Due to the bounded volume of environmental time-series data, deep neural networks overfit to transient noise.

The previous top-performing Random Forest model (v2) achieved $R^2 = 0.8318$ on holdout data, but suffered from a **14.13% overfitting gap** ($R^2_{\text{train}} = 0.9730$). Diagnostic analysis revealed that this overfit occurred because unconstrained decision trees (`max_depth=12`, `min_samples_leaf=1`) memorized specific training instances and local noise.

### 4.2.3 Breakthrough Performance of SPIME v4
The **Stacked Physics-Informed Meta-Ensemble (SPIME v4)** achieved state-of-the-art results:
- **Test Partition $R^2 = 0.9732$** and **Holdout $R^2 = 0.9632$**.
- **Mean Absolute Error (MAE)** reduced to **$0.61 \, \mu\text{g/m}^3$** (a **$66.3\%$ error reduction** compared to the previous best model's $1.81 \, \mu\text{g/m}^3$).
- **Root Mean Squared Error (RMSE)** reduced to **$1.23 \, \mu\text{g/m}^3$** (a **$53.2\%$ reduction**).
- **Overfitting Gap = $-0.0002$**: The 5-Fold out-of-fold cross-validation stacking matrix $S_{\text{train}}$ ensured that the `RidgeCV` meta-learner only evaluated predictions on data unseen by base models during training folds, completely eliminating data leakage.

---

## 4.3 Physical Interpretation of Kohler Growth and Atmospheric Features

Feature importance extraction from the SPIME v4 base estimators revealed that physical Kohler swelling parameters and thermodynamic moisture variables were the dominant drivers of sensor error correction:

1. **Multi-Gamma Kohler Growth Curves $f(\text{RH}, \gamma)$**: Accounted for over $35\%$ of total feature importance. By providing explicit mathematical formulations of water uptake $f(\text{RH}, \gamma) = \text{pm25} \cdot (1 - \text{RH}/100)^{-\gamma}$, decision trees were guided by physical laws rather than fitting arbitrary humidity splits.
2. **Absolute Humidity ($AH$) & Dew Point Depression**: Quantified the absolute water mass density in ambient air ($\text{g/m}^3$), enabling the model to distinguish between warm humid air and cool dry air at identical relative humidity levels.
3. **Multi-Window EWMA Trends (1h to 24h)**: Provided short-term temporal continuity, allowing the ensemble to smooth sensor micro-fluctuations while rapidly tracking real atmospheric pollution events.
4. **Harmattan Dust Storm Indicators**: Successfully compensated for Saharan mineral dust loadings during the dry season (November to March), preventing over-correction during low-humidity dust storms.

---

## 4.4 Summary

The SPIME v4 architecture establishes a new benchmark for low-cost PM2.5 sensor calibration in Sub-Saharan Africa. By integrating Kohler aerosol growth physics with 5-Fold cross-validated stacking, the model delivers reference-grade precision ($R^2 = 0.9732$, $\text{MAE} = 0.61 \, \mu\text{g/m}^3$) suitable for operational deployment at Afri-SET and municipal air quality networks across Accra.
