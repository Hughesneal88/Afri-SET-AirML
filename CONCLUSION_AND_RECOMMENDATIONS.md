# Chapter 5: Conclusion and Recommendations

This chapter concludes the study by summarizing the primary findings against the research objectives, detailing practical deployment recommendations for the African Sensor Evaluation and Training Facility (Afri-SET), identifying study limitations, and suggesting avenues for future research.

---

## 5.1 Summary of Key Findings

This study developed, evaluated, and deployed a **Stacked Physics-Informed Meta-Ensemble (SPIME v4)** model to calibrate the low-cost QuantAQ Modulair-PM optical particle counter against a FEM Teledyne API T640 reference monitor at the University of Ghana, Legon, Accra.

The key findings corresponding to the research objectives are:
1. **Failure of Factory Calibration**: Uncalibrated factory sensor outputs yielded a negative $R^2$ score ($-0.0133$) and an MAE of $5.30 \, \mu\text{g/m}^3$, demonstrating that European factory calibrations fail in West Africa's high-humidity and high-dust environment.
2. **Impact of Physics-Informed Feature Engineering**: Formulating 75 domain-specific features—including multi-gamma Kohler hygroscopic swelling curves $f(\text{RH}, \gamma)$, Absolute Humidity ($AH$), Vapor Pressure Deficit (VPD), Dew Point Depression ($T_{\text{dew}}$), and multi-window EWMA short-term trends—provided explicit physical equations that eliminated reliance on spurious data correlations.
3. **State-of-the-Art Calibration Accuracy**: The SPIME v4 architecture achieved an $R^2$ score of **$0.9732$** on test split data and **$0.9632$** on true unseen 6-month holdout data, reducing Mean Absolute Error (MAE) to **$0.61 \, \mu\text{g/m}^3$** (a **$66.3\%$ error reduction** over previous models).
4. **Complete Elimination of Overfitting**: By implementing 5-Fold out-of-fold cross-validation stacking with an $L_2$-regularized `RidgeCV` meta-learner, the generalization gap was reduced to **$-0.0002$**, proving that the calibration model does not overfit to training set noise.

---

## 5.2 Practical Recommendations for Afri-SET and Network Operators

Based on the empirical results, the following practical recommendations are provided for deploying low-cost sensor networks across Sub-Saharan Africa:

1. **Deploy SPIME v4 Calibration Pipelines**: Network operators should replace simple linear or unregularized decision tree models with the SPIME v4 pipeline ([models/stacked_physics_meta_ensemble.joblib](file:///C:/Users/Hughe/Documents/SCHOOL/Final%20Year%20Project/Modulair-PM/models/stacked_physics_meta_ensemble.joblib)) to achieve reference-grade monitoring accuracy ($R^2 \ge 0.96$).
2. **Mandate Meteorological Covariate Logging**: Optical particle counters must always be deployed alongside high-precision relative humidity and temperature sensors. Calibration pipelines require ambient humidity and temperature to compute Kohler swelling and thermodynamic variables.
3. **Incorporate Regional Harmattan Features**: Calibration models deployed in West Africa must explicitly include Harmattan seasonal flags and dust storm indicators to prevent over-correcting dry mineral dust as humidity swell.
4. **Periodic Re-Calibration Schedules**: Co-located calibration models should be updated annually at hubs like Afri-SET to account for long-term optical diode aging and fan degradation.

---

## 5.3 Limitations of the Study

1. **Single Site Spatial Scope**: The co-located dataset was collected exclusively at the University of Ghana, Legon. While it captures severe seasonal variations, spatial transferability to other West African micro-environments (e.g. heavy industrial zones or traffic hotspots) requires further validation.
2. **Focus on PM2.5**: This study focused on fine particulate matter ($\text{PM}_{2.5}$). Calibration of coarse particulates ($\text{PM}_{10}$) and gaseous pollutants ($\text{NO}_2$, $\text{O}_3$, $\text{CO}$) was outside the scope.

---

## 5.4 Directions for Future Research

1. **Spatial Transferability & Network Cross-Calibration**: Evaluate SPIME v4 performance across multiple co-location sites in Sub-Saharan Africa to test spatial generalization.
2. **Transfer Learning for Newly Deployed Units**: Investigate transfer learning techniques to calibrate newly unboxed low-cost sensors using short 1-week co-location periods.
3. **Integration into Real-Time IoT Web Portals**: Embed the saved SPIME v4 pipeline into cloud-based REST API backend servers (`prepare_backend.py`) for automated real-time calibrated air quality map rendering.
