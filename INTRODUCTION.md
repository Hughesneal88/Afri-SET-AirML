# Chapter 1: Introduction

## 1.1 Background and Motivation
Ambient air pollution is one of the most pressing global environmental health crises of the twenty-first century, contributing to millions of premature deaths annually. Among various air pollutants, fine particulate matter with an aerodynamic diameter of 2.5 micrometers or less ($\text{PM}_{2.5}$) is particularly hazardous. Because of its microscopic size, $\text{PM}_{2.5}$ can penetrate deep into the human respiratory system, enter the bloodstream, and lead to severe cardiovascular and respiratory diseases, including lung cancer, ischemic heart disease, and stroke.

Despite the severe public health implications of air pollution, monitoring infrastructure remains critically sparse globally, with the most severe data gaps concentrated in low- and middle-income regions. Sub-Saharan Africa (SSA), in particular, suffers from a severe deficit of continuous, high-quality air quality monitoring. Establishing and maintaining traditional reference-grade monitoring stations—such as Beta Attenuation Monitors (BAM) or optical spectroscopy systems like the Teledyne T640—requires prohibitive capital costs (often exceeding \$20,000 to \$30,000 per unit), specialized technical expertise, stable power grids, and regular calibration maintenance. Consequently, vast urban populations across West Africa live in areas without any active ambient air quality monitoring.

In response to this monitoring deficit, low-cost sensors (LCS) have emerged as a disruptive and promising technology. These devices, which typically rely on optical particle counters (OPCs) to measure light scattering by ambient dust and smoke, are highly portable, consume minimal power, and cost a fraction of reference instruments (typically \$200 to \$2,000). By deploying dense networks of LCS, municipal authorities and researchers can map air pollution at high spatial and temporal resolutions, identifying local hot spots and tracking exposure levels in real-time.

However, the widespread deployment of LCS is hindered by significant data quality concerns. Optical low-cost sensors do not measure mass directly; instead, they count particles based on light scattering and convert these counts to mass concentrations using mathematical assumptions about particle density and refractive index. As a result, LCS readings are highly sensitive to:
1. **Meteorological conditions**: High relative humidity (RH) causes hygroscopic growth, where particles absorb water and swell, leading to systematic overestimation of particle size and mass.
2. **Aerosol composition shifts**: Seasonal wind patterns, particularly the dry, dust-laden Harmattan winds originating from the Sahara Desert, alter the physical and optical properties of ambient aerosols, leading to significant sensor drift and calibration mismatches.
3. **Physical sensor degradation**: Dust accumulation, laser aging, and fan degradation cause baseline drift over time.

To address these limitations, it is critical to develop robust, localized, and season-aware calibration models. Machine learning (ML) offers a powerful framework for this task, as it can model complex, non-linear interactions between raw sensor outputs, temperature, humidity, and seasonal factors (such as the Harmattan winds).

---

## 1.2 Air Quality Challenges in Sub-Saharan Africa and West Africa
The West African sub-region, particularly coastal cities like Accra, Ghana, faces a complex mixture of air pollution sources and meteorological drivers:
- **Anthropogenic Sources**: Rapid urbanization and population growth have led to intensified vehicle emissions (often from older, poorly maintained diesel fleets), biomass burning for domestic cooking, open refuse burning, and industrial emissions.
- **Natural and Seasonal Sources**: The region is heavily impacted by the Harmattan, a seasonal dry wind that blows from the Sahara Desert southwest across West Africa between November and March. The Harmattan carries vast quantities of mineral dust, which drastically increases ambient $\text{PM}_{2.5}$ and $\text{PM}_{10}$ concentrations.
- **Meteorological Extremes**: Coastal West Africa experiences a tropical climate characterized by high year-round temperatures and alternating dry and wet monsoon seasons. High relative humidity during the wet season (often exceeding 80–90%) alters sensor responsiveness, while intense tropical rainfall events lead to atmospheric washout, rapidly scrubbing particulates from the boundary layer.

Standard factory calibrations for low-cost sensors, which are typically developed in temperate European or North American climates under low-humidity conditions with industrial combustion-dominated aerosols, fail catastrophically when deployed in West Africa. Under the high-humidity, high-dust conditions of Accra, uncalibrated LCS readings can deviate from reference instruments by over 100%.

---

## 1.3 The Afri-SET Initiative and the Modulair-PM Project
This research is situated within the active evaluation framework of the **African Sensor Evaluation and Training Facility (Afri-SET)**, based at the Department of Physics, University of Ghana, Legon. Afri-SET acts as a regional hub for evaluating low-cost air quality sensors under local meteorological and environmental conditions in Sub-Saharan Africa. The facility co-locates candidate low-cost sensors with regulatory-grade reference instruments, creating co-located datasets that enable the training and testing of localized calibration models.

This project focuses on calibrating the **QuantAQ Modulair-PM** sensor (specifically unit `MOD-PM-01068`), a low-cost ambient air quality monitor that houses an optical particle counter (OPC-N3) alongside meteorological sensors for relative humidity, temperature, and atmospheric pressure. By co-locating this sensor at the University of Ghana campus with a US EPA Federal Equivalent Method (FEM) reference monitor—the **Teledyne API T640**—a high-resolution hourly dataset spanning the years 2024 to 2025 was established. This multi-season dataset captures the two dominant meteorological end-members characteristic of the West African sub-region—from extreme humidity surges during the maritime West African Monsoon to heavy transboundary Saharan mineral dust episodes during the continental Harmattan season—providing an empirical foundation for training physics-informed machine learning models.

---

## 1.4 Problem Statement
Low-cost air quality sensors (such as the QuantAQ Modulair-PM) offer a scalable solution to the air quality data desert in Accra, Ghana. However, their raw measurements suffer from severe inaccuracies due to environmental interference (hygroscopic particle growth under high humidity) and seasonal composition changes (coarse Saharan mineral dust during the Harmattan). Existing calibration methods, such as simple linear corrections, fail to capture the non-linear, interactive, and temporally dependent relationships between meteorological covariates and sensor errors. Furthermore, specific Saharan dust loadings are rarely integrated into low-cost sensor calibration pipelines in West Africa. Without robust, machine learning-driven calibration models that explicitly incorporate local meteorological contexts (like relative humidity and seasonal Harmattan winds), the data generated by low-cost sensors remains inadequate for regulatory compliance, epidemiological studies, or policy-making.

---

## 1.5 Research Aim and Objectives

### 1.5.1 Primary Aim
The primary aim of this study is to develop, evaluate, and deploy machine learning-based calibration models that improve the measurement accuracy of the QuantAQ Modulair-PM low-cost sensor for ambient $\text{PM}_{2.5}$ prediction in Accra, Ghana, utilizing co-located reference data from a Teledyne T640 monitor.

### 1.5.2 Specific Objectives
1. **Establish a Co-located Database**: Align and preprocess hourly particulate and meteorological measurements from the QuantAQ Modulair-PM sensor and the Teledyne T640 reference monitor collected at the University of Ghana, Legon between 2024 and 2025.
2. **Engineer Physics-Informed Aerosol and Meteorological Features**: Formulate 75 domain-specific features, including multi-gamma Kohler hygroscopic swelling curves $f(\text{RH}, \gamma) = \text{pm25} \cdot (1 - \text{RH}/100)^{-\gamma}$, Absolute Humidity ($AH$), Vapor Pressure Deficit (VPD), Dew Point Temperature ($T_{\text{dew}}$), multi-window EWMA short-term trends (1h to 24h), cyclical temporal harmonics, and seasonal Harmattan dust indicators.
3. **Develop a Stacked Physics-Informed Meta-Ensemble (SPIME v4)**: Construct and tune a high-performance calibration pipeline combining four diverse base estimators (Random Forest, ExtraTrees, LightGBM, HistGradientBoosting) with 5-Fold out-of-fold cross-validated stacking and an $L_2$-regularized `RidgeCV` meta-learner.
4. **Validate Generalization and Eliminate Overfitting**: Evaluate model performance across chronological splits and unseen 6-month holdout datasets to achieve reference-grade predictive accuracy ($R^2 = 0.9732$ on test split, $R^2 = 0.9632$ on unseen holdout, $\text{MAE} = 0.61 \, \mu\text{g/m}^3$) with zero overfitting gap ($-0.0002$).
5. **Analyze Feature Importances and Residuals**: Perform diagnostic error analysis, residual tests (normality and homoscedasticity), and interpret feature importances to understand the physical and environmental drivers of sensor error correction.

---

## 1.6 Scope of the Study
This study is limited to the calibration of the QuantAQ Modulair-PM sensor (unit `MOD-PM-01068`) co-located at the Department of Physics, University of Ghana, Legon, Accra. The analysis utilizes hourly data collected over the 2024–2025 period. Reference measurements are restricted to the co-located Teledyne API T640 Federal Equivalent Method (FEM) optical mass monitor. Environmental covariates include localized relative humidity, ambient temperature, barometric pressure, and a calculated regional Harmattan score. This study does not evaluate sensor spatial generalization to other geographic regions outside Accra, nor does it address calibration of gaseous pollutants (such as $\text{NO}_x$ or $\text{O}_3$).

---

## 1.7 Structure of the Thesis
The remainder of this thesis is structured as follows:
- **Chapter 2: Literature Review** conducts a detailed review of air pollution monitoring challenges, the working mechanisms of optical particle counters, environmental and meteorological interferences, existing machine learning calibration literature, and the unique atmospheric dynamics of the West African region.
- **Chapter 3: Methodology** describes the experimental co-location setup, data preprocessing steps, feature engineering methods, the mathematical formulation of the machine learning algorithms (Random Forest and Neural Networks), the time-series validation strategy, and model evaluation metrics.
- **Chapter 4: Results and Discussion** presents the model performances, comparative metrics, feature importance rankings, residual diagnostic plots, and a discussion of the models' behavior during the Harmattan and wet seasons.
- **Chapter 5: Conclusion and Recommendations** summarizes the key findings, details the practical implementation considerations for Afri-SET, outlines the limitations of the study, and recommends directions for future research.
