# Chapter 2: Literature Review

## 2.1 Fine Particulate Matter ($\text{PM}_{2.5}$) and the Sub-Saharan African Context
Ambient particulate matter, specifically $\text{PM}_{2.5}$ (particles with an aerodynamic diameter $\le 2.5\ \mu\text{g/m}^3$), is recognized as a major risk factor for global morbidity and mortality. Long-term exposure to elevated $\text{PM}_{2.5}$ is epidemiologically linked to cardiovascular dysfunction, chronic obstructive pulmonary disease (COPD), respiratory infections, and systemic inflammation (Mauderly et al., 2008). 

In Sub-Saharan Africa (SSA), the burden of air pollution-related disease is particularly severe due to the co-existence of heavy anthropogenic emissions (vehicle exhaust, domestic biomass burning, waste combustion) and natural aerosol sources. However, the region is characterized by an extreme "data desert" regarding air quality monitoring. Establishing a representative regulatory-grade monitoring network is often impossible for local governments due to high capital expenditures, complex maintenance schedules, stable energy requirements, and the necessity of highly trained personnel (DeSouza et al., 2017). Consequently, low-cost sensors (LCS) have been widely identified as the most viable mechanism to democratize air quality monitoring, provide localized spatial coverage, and protect public health.

---

## 2.2 Low-Cost Sensors vs. Reference Instruments
To evaluate the reliability of low-cost sensors, it is necessary to contrast their operating principles with reference-grade monitors.

### 2.2.1 Optical Particle Counters (OPCs) in LCS
Low-cost PM sensors, such as the QuantAQ Modulair-PM (which utilizes the Alphasense OPC-N3), typically operate using light scattering technologies. Inside the sensor, a sample of ambient air is drawn through a sensing chamber by a fan or pump. A laser beam illuminates the incoming stream of particles. When a particle intersects the laser beam, it scatters light, which is measured by a photo-diode detector positioned at a specific scattering angle. 

The sensor counts individual light pulses (indicating particle count) and correlates the amplitude of the scattered light pulse with particle size based on Mie Scattering Theory. The particle counts are grouped into discrete size categories (known as "bins"). To convert these counts into mass concentration ($\mu\text{g/m}^3$), the device applies the following mathematical conversion:
$$\text{Mass} = \sum_{i} N_i \times V_i \times \rho_i$$
where $N_i$ is the number concentration of bin $i$, $V_i$ is the average volume of particles in bin $i$ (under the assumption that all particles are perfectly spherical), and $\rho_i$ is the assumed particle density. 

This conversion process introduces systematic errors because:
- **Refractive Index Assumption**: The intensity of scattered light depends heavily on the refractive index of the aerosol. LCS algorithms assume a constant refractive index, which varies significantly in real-world mixtures of black carbon, mineral dust, and organic aerosols.
- **Spherical Shape Assumption**: Mineral dust particles are highly irregular and non-spherical, violating the spherical volume assumption and causing sizing errors.
- **Density Assumption**: A uniform density is assumed (typically around $1.65\ \text{g/cm}^3$), whereas carbonaceous soot ($1.0\text{--}1.2\ \text{g/cm}^3$) and Saharan mineral dust ($2.5\text{--}2.7\ \text{g/cm}^3$) have vastly different densities.

### 2.2.2 Reference-Grade Monitors: Teledyne API T640
In contrast, reference-grade instruments utilize more sophisticated, stable, and highly calibrated optical and physical methods. The Teledyne API T640 is a continuous particulate monitor that uses broad-spectrum white LED light-scattering spectroscopy to determine particulate mass concentrations. It measures light scattering over a wide range of angles and utilizes advanced refractive index compensation algorithms, enabling it to accurately size and count particles without the extreme sensitivity to chemical composition changes seen in low-cost sensors. The T640 is designated as a US EPA Federal Equivalent Method (FEM) for $\text{PM}_{2.5}$ and $\text{PM}_{10}$ monitoring, providing a highly reliable "ground truth" benchmark.

---

## 2.3 Environmental and Meteorological Interferences
Meteorological conditions exert a dominant influence on uncalibrated optical sensor readings, causing significant deviations from reference measurements.

### 2.3.1 Relative Humidity (RH) and Aerosol Hygroscopicity
The most significant meteorological driver of optical sensor error is relative humidity. Many atmospheric aerosols are hygroscopic, meaning they absorb moisture from the surrounding air. As relative humidity increases, particularly past the **Deliquescence Relative Humidity (DRH)** threshold (typically between 70% and 80%), particles undergo rapid hygroscopic growth. They absorb water, swell in size, and change their refractive index (approaching that of pure water, $1.33$).

Because uncalibrated optical sensors cannot distinguish between a dry particulate and an water-swollen aerosol, they classify these grown particles into larger size bins and calculate a vastly inflated mass concentration. The relationship between dry particulate mass and relative humidity is often modeled using the $f(\text{RH})$ correction factor:
$$PM_{\text{observed}} = PM_{\text{dry}} \times f(\text{RH})$$
$$f(\text{RH}) = 1 + \kappa \left( \frac{\text{RH}}{100 - \text{RH}} \right)$$
where $\kappa$ represents the hygroscopic growth parameter of the aerosol mixture. In highly humid tropical environments like Accra, uncorrected hygroscopic growth is a major source of positive measurement bias.

### 2.3.2 Temperature and Volatilization
Ambient temperature affects both the physical state of the aerosol and the internal electronics of the sensor. High temperatures can cause the volatilization of semi-volatile organic compounds and ammonium nitrate from the aerosol phase to the gas phase, reducing the particulate mass measured by reference instruments but potentially leaving raw counts unchanged in optical sensors. Additionally, temperature fluctuations can affect laser diode stability and photo-detector response, necessitating temperature compensation in calibration models.

### 2.3.3 The Harmattan Wind and Saharan Mineral Dust
The dry winter season (November to March) in West Africa is dominated by the Harmattan winds. These trade winds transport vast quantities of coarse Saharan mineral dust across the sub-region. The Harmattan is characterized by:
- **Massive PM spikes**: Ambient $\text{PM}_{2.5}$ and $\text{PM}_{10}$ concentrations routinely exceed $100\ \mu\text{g/m}^3$ and can reach up to $500\ \mu\text{g/m}^3$.
- **Low humidity**: Relative humidity drops to extremely low levels (often $<20\%$).
- **Coarse dust fraction**: The aerosol distribution shifts toward larger, highly non-spherical, high-density mineral particles.

Under Harmattan conditions, optical particle counters face **optical saturation** and **coincidence errors** (where multiple particles pass through the laser beam simultaneously, registering as a single large particle). Furthermore, the high density ($>2.5\ \text{g/cm}^3$) and highly irregular shapes of dust particles violate the standard assumptions of the LCS mass conversion algorithm, causing uncalibrated sensors to underestimate the actual mass concentration. Thus, incorporating a "Harmattan Score" or seasonal indicator is essential for calibration models in West Africa.

---

## 2.4 Sensor Calibration Paradigms and Machine Learning
To correct these environmental biases, researchers co-locate low-cost sensors with reference instruments to build mathematical calibration models.

### 2.4.1 Classical Regression Models
Initial calibration attempts relied on Simple Linear Regression (SLR) or Multiple Linear Regression (MLR), expressing corrected PM as a linear combination of raw PM, temperature, and relative humidity:
$$\text{PM}_{\text{calibrated}} = \beta_0 + \beta_1 \text{PM}_{\text{raw}} + \beta_2 T + \beta_3 \text{RH}$$
While computationally simple, linear regression models fail to capture the non-linear, exponential behavior of hygroscopic particle growth at high relative humidity ($>80\%$) and cannot model the complex interaction terms between temperature, humidity, wind patterns, and aerosol types.

### 2.4.2 Machine Learning Regressors
To overcome the limitations of linear models, recent literature has shifted toward non-linear machine learning architectures:
- **Random Forest (RF)**: Random Forest is an ensemble learning method that constructs a multitude of decision trees during training. It is highly robust, handles non-linear interactions natively, and is resilient to outliers. RF models have consistently outperformed linear models in sensor calibration studies, achieving high $R^2$ scores by mapping environmental variables to sensor error corrections.
- **Multi-Layer Perceptron (MLP) Neural Networks**: Artificial Neural Networks (ANNs) are capable of approximating any continuous non-linear function. By training multi-layer perceptrons with backpropagation, the model can automatically discover complex features and interaction terms from input variables (sensor PM, temperature, humidity, and temporal features). However, they require careful tuning of hidden layer sizes, activation functions, and regularization parameters to prevent overfitting.
- **Gradient Boosting (XGBoost/LightGBM)**: Sequential ensemble models that build decision trees iteratively to minimize residual error. They often yield marginal performance improvements over Random Forest but can be sensitive to hyperparameter configurations and missing values.

### 2.4.3 Validation Strategies and Data Leakage
In time-series calibration datasets, environmental conditions are highly autocorrelated (i.e., temperature at hour $t$ is highly correlated with temperature at hour $t+1$). Standard random train-test splits (such as `train_test_split` with shuffle) lead to **data leakage**, where adjacent hours are split between the training and testing sets. This results in overly optimistic validation metrics that fail to reflect the model's actual performance when deployed to future unseen data. To ensure robust evaluation, recent research highlights the necessity of using **chronological splits** (e.g., training on 2024 data and testing on 2025 data) and **time-series cross-validation**, where the validation fold always succeeds the training fold in time.
