"""
Afri-SET Low-Cost Air Quality Sensor Catalog & SPIME Transferability Knowledge Base
=====================================================================================
Comprehensive repository of all 33 low-cost sensor models evaluated and published
by the African Sensor Evaluation and Training (Afri-SET) facility at the
Department of Physics, University of Ghana, Legon (Accra, Ghana).

Includes:
- Complete metadata across Cohort 1, Cohort 2, and Cohort 3.
- Core optical sensing architectures (Alphasense OPC-N3, Plantower, Sensirion, Nova SDS011, etc.).
- Afri-SET seasonal evaluation performance (Wet Monsoon R² vs Dry Harmattan R²).
- Official PDF evaluation reports (AWS S3).
- SPIME model transferability and adaptation guidelines for every sensor class.
"""

import re

AFRISET_SENSORS = [
    # ─────────────────────────────────────────────────────────────────────────────
    # FIRST COHORT (12 SENSORS)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "habitatmap_airbeam3",
        "cohort": "First Cohort",
        "title": "HabitatMap AirBeam3",
        "model_name": "Airbeam3",
        "manufacturer": "HabitatMap",
        "optical_core": "Plantower PMS7003",
        "optical_architecture": "Laser light scattering photodiode with 6 discrete size bins (>0.3, >0.5, >1.0, >2.5, >5.0, >10 µm)",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Temperature", "Relative Humidity"],
        "telemetry": "BLE, Wi-Fi, Cellular 4G, Mobile/Stationary",
        "description": "Palm-sized air quality sensor that measures particulate matter using a Plantower laser scattering sensor alongside onboard temperature and humidity. Popular for mobile wearable mapping and grassroots monitoring.",
        "manufacturer_link": "https://www.habitatmap.org/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Airbeam3+sensors.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforAirbeam3.pdf",
        "wet_season_metrics": {"r2": 0.83, "slope": 4.31, "intercept": -3.92, "mae": 5.16},
        "dry_season_metrics": {"r2": 0.64, "slope": 21.84, "intercept": 21.76, "mae": 28.50},
        "transfer_family": "plantower"
    },
    {
        "id": "iqair_airvisual_outdoor",
        "cohort": "First Cohort",
        "title": "IQAir AirVisual Outdoor",
        "model_name": "IQAir",
        "manufacturer": "IQAir",
        "optical_core": "Dual Laser Optical Particulate Sensor",
        "optical_architecture": "Dual redundant laser light scattering chambers with cross-channel discrepancy monitoring",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO2", "Temperature", "Relative Humidity", "Barometric Pressure"],
        "telemetry": "Wi-Fi, Ethernet, 4G LTE",
        "description": "Weather-proof outdoor monitoring station featuring dual laser particulate sensors for internal self-checking, temperature-controlled intake, and automated calibration against regional air quality networks.",
        "manufacturer_link": "https://www.iqair.com/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+IQair+sensors.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforIQairsensors.pdf",
        "wet_season_metrics": {"r2": 0.82, "slope": 1.12, "intercept": 2.10, "mae": 4.80},
        "dry_season_metrics": {"r2": 0.71, "slope": 1.45, "intercept": 6.30, "mae": 14.20},
        "transfer_family": "dual_laser"
    },
    {
        "id": "airly_pm",
        "cohort": "First Cohort",
        "title": "Airly PM",
        "model_name": "Airly",
        "manufacturer": "Airly",
        "optical_core": "Laser Photometer Particle Counter",
        "optical_architecture": "Miniature optical scattering cell with integrated inlet heater for moisture mitigation",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Temperature", "Relative Humidity", "Atmospheric Pressure"],
        "telemetry": "GSM / LTE-M",
        "description": "Compact municipal sensor node equipped with an internal heating element to reduce ambient humidity artifacts before light scattering measurement.",
        "manufacturer_link": "https://airly.org/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Airly+sensor.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforAirly.pdf",
        "wet_season_metrics": {"r2": 0.79, "slope": 0.95, "intercept": 3.40, "mae": 5.90},
        "dry_season_metrics": {"r2": 0.68, "slope": 1.62, "intercept": 8.70, "mae": 18.40},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "quantaq_modulair_pm",
        "cohort": "First Cohort",
        "title": "QuantAQ MODULAIR-PM",
        "model_name": "Modulair",
        "manufacturer": "QuantAQ",
        "optical_core": "Alphasense OPC-N3 (24 size bins)",
        "optical_architecture": "Single-particle light scattering spectrometer binning particles from 0.35 µm to 40 µm across 24 channels with high-volume sampling pump",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Particle Number Distribution (24 bins)", "Temperature", "Relative Humidity", "Pressure", "Dew Point"],
        "telemetry": "Cellular 4G LTE, Wi-Fi, MicroSD, Cloud REST API",
        "description": "The primary target sensor of this thesis research (unit MOD-PM-01068). High-grade optical research instrument co-located with the Teledyne T640 at the Afri-SET facility. Highly sensitive to hygroscopic growth during monsoon humidity and optical saturation during Harmattan dust.",
        "manufacturer_link": "https://www.quantaq.com/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/MODULAR+AIR+Field+evaluation+.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/MODULARPM10.pdf",
        "wet_season_metrics": {"r2": 0.81, "slope": 1.25, "intercept": -1.40, "mae": 4.10},
        "dry_season_metrics": {"r2": 0.74, "slope": 1.55, "intercept": 12.10, "mae": 15.30},
        "transfer_family": "alphasense_opc"
    },
    {
        "id": "south_coast_science_praxis_urban",
        "cohort": "First Cohort",
        "title": "South Coast Science Praxis/Urban",
        "model_name": "Praxis/Urban",
        "manufacturer": "South Coast Science",
        "optical_core": "Alphasense OPC-N3",
        "optical_architecture": "Alphasense OPC-N3 optical particle counter paired with Alphasense electrochemical AFE gas sensors",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "Temperature", "Relative Humidity"],
        "telemetry": "Cellular 4G, GPS, Linux SBC (Raspberry Pi Compute Module)",
        "description": "Industrial-grade multipollutant monitor combining the Alphasense OPC-N3 with four electrochemical gas sensors in an ultra-rugged IP66 enclosure running open-source environmental firmware.",
        "manufacturer_link": "https://www.southcoastscience.com/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+PRAXIS_Urban+Sensors.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforPRAXIS.pdf",
        "wet_season_metrics": {"r2": 0.80, "slope": 1.18, "intercept": 1.80, "mae": 4.60},
        "dry_season_metrics": {"r2": 0.72, "slope": 1.48, "intercept": 9.50, "mae": 16.80},
        "transfer_family": "alphasense_opc"
    },
    {
        "id": "airquality_egg",
        "cohort": "First Cohort",
        "title": "AirQuality Egg",
        "model_name": "Air Quality Egg",
        "manufacturer": "Wicked Device",
        "optical_core": "Optical Particle Counter",
        "optical_architecture": "Compact light scattering PM sensor module with optional metal-oxide / electrochemical gas sensors",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "VOC", "CO2", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, Ethernet",
        "description": "Community science and educational sensor node designed for indoor/outdoor environmental sensing with cloud dashboard integration.",
        "manufacturer_link": "https://airqualityegg.com/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+AQE+sensors.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforAQEsensors.pdf",
        "wet_season_metrics": {"r2": 0.76, "slope": 0.88, "intercept": 4.20, "mae": 6.80},
        "dry_season_metrics": {"r2": 0.61, "slope": 1.80, "intercept": 14.20, "mae": 22.10},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "sensors_africa",
        "cohort": "First Cohort",
        "title": "Sensors.Africa",
        "model_name": "Sensors.Africa",
        "manufacturer": "Code for Africa / Sensor.Community",
        "optical_core": "Nova Fitness SDS011",
        "optical_architecture": "Diode laser light scattering chamber measuring forward scattered light across two integrated mass channels (PM2.5 and PM10)",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity (via DHT22/BME280)"],
        "telemetry": "Wi-Fi, NodeMCU ESP8266, open data portal",
        "description": "DIY grassroots citizen science air quality monitor based on the open Sensor.Community architecture widely deployed across African cities for community air monitoring.",
        "manufacturer_link": "https://sensors.africa/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Sensor.Africa.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforSensor.Africa.pdf",
        "wet_season_metrics": {"r2": 0.74, "slope": 0.82, "intercept": 5.10, "mae": 7.30},
        "dry_season_metrics": {"r2": 0.59, "slope": 2.10, "intercept": 18.50, "mae": 26.40},
        "transfer_family": "nova_sds011"
    },
    {
        "id": "airqo_binos",
        "cohort": "First Cohort",
        "title": "AirQO Binos",
        "model_name": "Binos",
        "manufacturer": "AirQo (Makerere University, Uganda)",
        "optical_core": "Dual Plantower PMS5003",
        "optical_architecture": "Twin Plantower PMS5003 optical scattering sensors in parallel for automated inter-sensor fault detection",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity", "Barometric Pressure"],
        "telemetry": "2G / GPRS, Solar powered, Cloud platform",
        "description": "Locally engineered Sub-Saharan African air monitor developed by AirQo at Makerere University, optimized for tropical heat, dust storms, and intermittent cellular connectivity.",
        "manufacturer_link": "https://airqo.net/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+AirQo_2.5.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforAirQo.pdf",
        "wet_season_metrics": {"r2": 0.82, "slope": 1.15, "intercept": 1.60, "mae": 4.90},
        "dry_season_metrics": {"r2": 0.67, "slope": 1.58, "intercept": 11.20, "mae": 17.50},
        "transfer_family": "plantower"
    },
    {
        "id": "tsi_bluesky_8145",
        "cohort": "First Cohort",
        "title": "TSI BlueSky 8145",
        "model_name": "BlueSky",
        "manufacturer": "TSI Incorporated",
        "optical_core": "TSI Precision Optical Sensor",
        "optical_architecture": "Laser photometer with factory-calibrated gravimetric baseline alignment and heated intake protection",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, Cellular, TSI Link cloud",
        "description": "High-accuracy commercial sensor from leading aerosol instrumentation manufacturer TSI, featuring robust temperature and humidity compensation algorithms.",
        "manufacturer_link": "https://tsi.com/products/environmental-air-monitors/bluesky-air-quality-monitor/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+TSI-Bluesky+2.5.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforTSI-Bluesky.pdf",
        "wet_season_metrics": {"r2": 0.85, "slope": 1.08, "intercept": 0.80, "mae": 3.70},
        "dry_season_metrics": {"r2": 0.73, "slope": 1.35, "intercept": 7.40, "mae": 13.60},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "airgradient_outdoor_c1",
        "cohort": "First Cohort",
        "title": "AirGradient Outdoor",
        "model_name": "AirGradient",
        "manufacturer": "AirGradient",
        "optical_core": "Plantower PMS5003",
        "optical_architecture": "Plantower PMS5003 laser particle counter paired with Sensirion SHT40 temperature/humidity sensor",
        "measured_pollutants": ["PM2.5", "CO2 (Senseair S8)", "TVOC", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, Open-source ESP32 firmware",
        "description": "Fully open-hardware, open-source outdoor environmental monitor widely utilized in schools, universities, and research institutes.",
        "manufacturer_link": "https://www.airgradient.com/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Airgradient+sensors.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforAirgradient.pdf",
        "wet_season_metrics": {"r2": 0.83, "slope": 1.14, "intercept": 1.90, "mae": 4.80},
        "dry_season_metrics": {"r2": 0.65, "slope": 1.65, "intercept": 12.80, "mae": 19.10},
        "transfer_family": "plantower"
    },
    {
        "id": "clarity_node_s",
        "cohort": "First Cohort",
        "title": "Clarity Node-S",
        "model_name": "Node S",
        "manufacturer": "Clarity Movement",
        "optical_core": "Plantower PMS6003",
        "optical_architecture": "Low-profile laser particle scattering module with solar panel integration and cloud calibration",
        "measured_pollutants": ["PM2.5", "PM10", "NO2 (optional electrochemical)", "Temperature", "Relative Humidity"],
        "telemetry": "Native Cellular 2G/3G/4G, Solar powered, Battery backed",
        "description": "Turnkey commercial air quality sensing node deployed globally for municipal and regulatory monitoring networks, featuring proprietary cloud calibration algorithms.",
        "manufacturer_link": "https://www.clarity.io/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Clarity+Node+sensor.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforCLARITYsensors.pdf",
        "wet_season_metrics": {"r2": 0.84, "slope": 1.10, "intercept": 1.20, "mae": 4.20},
        "dry_season_metrics": {"r2": 0.70, "slope": 1.42, "intercept": 8.90, "mae": 14.80},
        "transfer_family": "plantower"
    },
    {
        "id": "kunak_air_pro",
        "cohort": "First Cohort",
        "title": "Kunak Air Pro",
        "model_name": "Kunak",
        "manufacturer": "Kunak Technologies",
        "optical_core": "High-Precision Optical Particle Counter",
        "optical_architecture": "Laser particle counter with smart gas sensor cartridges and internal climate control",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "SO2", "VOC", "Temperature", "Relative Humidity", "Pressure"],
        "telemetry": "2G/3G/4G, Ethernet, Solar / Mains power",
        "description": "High-end European indicative air monitoring station designed for regulatory compliance and environmental agency deployments.",
        "manufacturer_link": "https://www.kunak.es/",
        "pm25_report": "https://afriset-files.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Kunak+Air+Pro+PM2.5.pdf",
        "pm10_report": "https://pm10report.s3.eu-west-2.amazonaws.com/FieldevaluationforKunak10.pdf",
        "wet_season_metrics": {"r2": 0.86, "slope": 1.05, "intercept": 0.90, "mae": 3.40},
        "dry_season_metrics": {"r2": 0.76, "slope": 1.28, "intercept": 6.10, "mae": 12.10},
        "transfer_family": "laser_photometer"
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # SECOND COHORT (8 SENSORS)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "atmotube_pro",
        "cohort": "Second Cohort",
        "title": "Atmotube Pro",
        "model_name": "Atmotube",
        "manufacturer": "NotAnotherOne",
        "optical_core": "Sensirion SPS30",
        "optical_architecture": "Laser scattering optical counter with 5 discrete particle count bins (0.3-0.5, 0.5-1.0, 1.0-2.5, 2.5-4.0, 4.0-10 µm) and automated fan-cleaning mechanism",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "VOC", "Temperature", "Relative Humidity", "Atmospheric Pressure"],
        "telemetry": "BLE, USB-C, Portable Lithium Battery",
        "description": "Compact personal and portable air quality tracker utilizing the Sensirion SPS30 optical engine with MCERTS certification standards.",
        "manufacturer_link": "https://atmotube.com/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field+evaluation+for+Atmostube+PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.83, "slope": 1.15, "intercept": 2.20, "mae": 4.50},
        "dry_season_metrics": {"r2": 0.64, "slope": 1.68, "intercept": 13.50, "mae": 19.80},
        "transfer_family": "sensirion_sps30"
    },
    {
        "id": "redspira",
        "cohort": "Second Cohort",
        "title": "Redspira",
        "model_name": "Redspira",
        "manufacturer": "Redspira (Mexico)",
        "optical_core": "Plantower PMS5003",
        "optical_architecture": "Plantower PMS5003 laser light scattering counter integrated with weather sensors",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, Solar/Mains, Open community network",
        "description": "Community air quality sensor deployed widely across Latin America and international testbeds for public health tracking.",
        "manufacturer_link": "https://redspira.org/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field_Evaluation+_Report_on_Redspira_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.81, "slope": 1.18, "intercept": 2.50, "mae": 5.10},
        "dry_season_metrics": {"r2": 0.62, "slope": 1.72, "intercept": 14.80, "mae": 21.20},
        "transfer_family": "plantower"
    },
    {
        "id": "sensit_ramp",
        "cohort": "Second Cohort",
        "title": "Sensit RAMP",
        "model_name": "Sensit Ramp",
        "manufacturer": "Sensit Technologies",
        "optical_core": "Alphasense OPC-N2 / OPC-N3 + Plantower",
        "optical_architecture": "Multi-pollutant platform combining optical particle counting with 4-electrode electrochemical cells",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "SO2", "CO2", "Temperature", "Relative Humidity"],
        "telemetry": "Cellular, Solar power, SD Card",
        "description": "Rugged multipollutant monitor developed in collaboration with Carnegie Mellon University, widely utilized in academic air quality studies across Africa.",
        "manufacturer_link": "https://www.gasleaksensors.com/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field_Evaluation_Report_on_Sensit_Ramp_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.85, "slope": 1.08, "intercept": 1.10, "mae": 3.80},
        "dry_season_metrics": {"r2": 0.75, "slope": 1.32, "intercept": 6.80, "mae": 12.90},
        "transfer_family": "alphasense_opc"
    },
    {
        "id": "airgradient_outdoor_c2",
        "cohort": "Second Cohort",
        "title": "AirGradient Outdoor (v2)",
        "model_name": "Airgradient Outdoor",
        "manufacturer": "AirGradient",
        "optical_core": "Dual Plantower PMS5003",
        "optical_architecture": "Upgraded open-hardware platform with dual optical sensor bays for redundancy and accuracy verification",
        "measured_pollutants": ["PM2.5", "PM10", "CO2", "TVOC", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, ESP32-C3, MQTT / HTTP API",
        "description": "Second-generation AirGradient outdoor monitor featuring dual particulate sensors and enhanced tropical weatherproofing.",
        "manufacturer_link": "https://www.airgradient.com/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field_Evaluation_Report_on_AirGradient_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.84, "slope": 1.11, "intercept": 1.70, "mae": 4.40},
        "dry_season_metrics": {"r2": 0.66, "slope": 1.62, "intercept": 11.90, "mae": 18.20},
        "transfer_family": "plantower"
    },
    {
        "id": "atmos_nimo",
        "cohort": "Second Cohort",
        "title": "Atmos-Nimo",
        "model_name": "Atmos-Nimo",
        "manufacturer": "Respirer Living Sciences (India)",
        "optical_core": "Laser Particulate Counter",
        "optical_architecture": "Laser light scattering sensor with real-time temperature/humidity compensation and GPS tracking",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity", "Atmospheric Pressure"],
        "telemetry": "GSM 4G, GPS, Cloud API",
        "description": "Indian environmental sensor node engineered for high-dust, high-humidity South Asian and Sub-Saharan African conditions.",
        "manufacturer_link": "https://respirer.in/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field_Evaluation+_Report_on_Atmos_Nimo_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.79, "slope": 1.21, "intercept": 3.10, "mae": 5.80},
        "dry_season_metrics": {"r2": 0.61, "slope": 1.75, "intercept": 15.20, "mae": 22.80},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "purpleair_pa_ii_classic",
        "cohort": "Second Cohort",
        "title": "PurpleAir PA-II Classic",
        "model_name": "PA-II Classic",
        "manufacturer": "PurpleAir",
        "optical_core": "Dual Plantower PMS5003 (Channels A & B)",
        "optical_architecture": "Twin Plantower PMS5003 laser light counters mounted side-by-side with continuous inter-channel Pearson r verification",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Channel A & B raw bins", "Temperature (BME280)", "Relative Humidity", "Pressure"],
        "telemetry": "Wi-Fi, ESP8266, PurpleAir Open Real-Time Map",
        "description": "The world's most ubiquitous community air quality sensor. Provides dual optical channels to detect channel clog or drift. Extensively calibrated with US EPA non-linear relative humidity formulas.",
        "manufacturer_link": "https://www2.purpleair.com/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field+Evaluation+Report+for+PA-II-Classic_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.85, "slope": 1.10, "intercept": 1.40, "mae": 4.10},
        "dry_season_metrics": {"r2": 0.68, "slope": 1.55, "intercept": 10.40, "mae": 16.50},
        "transfer_family": "plantower"
    },
    {
        "id": "purpleair_pa_ii_flex",
        "cohort": "Second Cohort",
        "title": "PurpleAir PA-II Flex",
        "model_name": "PA-II Flex",
        "manufacturer": "PurpleAir",
        "optical_core": "Dual Plantower PMS5003 (Channels A & B)",
        "optical_architecture": "Twin Plantower PMS5003 laser light counters with local SD card logging and expanded telemetry ports",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Channels A & B", "Temperature", "Relative Humidity", "Pressure"],
        "telemetry": "Wi-Fi, MicroSD offline logging, Battery backup",
        "description": "Enhanced PurpleAir variant featuring local offline SD card backup logging, ideal for regions with intermittent power and Wi-Fi networks.",
        "manufacturer_link": "https://www2.purpleair.com/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field+Evaluation+Report+for+PA-II-Flex_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.86, "slope": 1.09, "intercept": 1.30, "mae": 3.90},
        "dry_season_metrics": {"r2": 0.69, "slope": 1.52, "intercept": 9.80, "mae": 15.90},
        "transfer_family": "plantower"
    },
    {
        "id": "zefan",
        "cohort": "Second Cohort",
        "title": "ZeFan",
        "model_name": "ZeFan",
        "manufacturer": "ZeFan Environmental",
        "optical_core": "Laser Light Scattering Sensor",
        "optical_architecture": "Low-power optical particulate detection module",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity"],
        "telemetry": "Cellular, Solar / Battery",
        "description": "Indicative optical dust monitor evaluated by Afri-SET for regional outdoor particulate monitoring in West Africa.",
        "manufacturer_link": "https://afriset.org/",
        "pm25_report": "https://secondcohortpm2report.s3.eu-west-2.amazonaws.com/Field_Evaluation+_Report_on_Zefan_PM2.5.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.78, "slope": 1.25, "intercept": 3.60, "mae": 6.20},
        "dry_season_metrics": {"r2": 0.58, "slope": 1.85, "intercept": 16.80, "mae": 24.50},
        "transfer_family": "laser_photometer"
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # THIRD COHORT (13 SENSORS)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "aqmesh_hi",
        "cohort": "Third Cohort",
        "title": "AQMesh Heated Inlet Sensor",
        "model_name": "AQMesh-HI",
        "manufacturer": "Environmental Instruments Ltd",
        "optical_core": "Optical Particle Counter with Heated Inlet",
        "optical_architecture": "Optical light scatter counter coupled with an active heated sample inlet to evaporate water before particle sizing",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "SO2", "CO2", "Temperature", "Relative Humidity", "Pressure"],
        "telemetry": "Cellular LTE, Battery / Solar, Cloud API",
        "description": "High-end UK indicative air quality station equipped with an active heated sample inlet, preventing hygroscopic droplet swelling above 75% RH.",
        "manufacturer_link": "https://www.aqmesh.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforAQMESHHIPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.88, "slope": 1.02, "intercept": 0.50, "mae": 2.90},
        "dry_season_metrics": {"r2": 0.78, "slope": 1.20, "intercept": 5.20, "mae": 10.80},
        "transfer_family": "heated_inlet_opc"
    },
    {
        "id": "aqmesh_s",
        "cohort": "Third Cohort",
        "title": "AQMesh Standard Sensor",
        "model_name": "AQMesh-S",
        "manufacturer": "Environmental Instruments Ltd",
        "optical_core": "Optical Particle Counter (Standard Inlet)",
        "optical_architecture": "Ambient temperature optical scattering counter with proprietary software humidity correction",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "Gases", "Temperature", "Relative Humidity", "Pressure"],
        "telemetry": "Cellular LTE, Battery powered",
        "description": "Standard unheated AQMesh sensor node, demonstrating the impact of high tropical relative humidity when active inlet heating is omitted.",
        "manufacturer_link": "https://www.aqmesh.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforAQMESHPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.82, "slope": 1.16, "intercept": 1.80, "mae": 4.60},
        "dry_season_metrics": {"r2": 0.72, "slope": 1.38, "intercept": 7.80, "mae": 14.20},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "aurassure_sensor",
        "cohort": "Third Cohort",
        "title": "Aurassure Sensor",
        "model_name": "Aurassure",
        "manufacturer": "Aurassure (India)",
        "optical_core": "IoT Laser Scattering Particulate Counter",
        "optical_architecture": "Laser light scattering sensor paired with smart meteorological sensors",
        "measured_pollutants": ["PM2.5", "PM10", "CO", "NO2", "SO2", "Temperature", "Relative Humidity"],
        "telemetry": "GSM 4G, LoRaWAN, Cloud dashboard",
        "description": "IoT-enabled smart city environmental monitor designed for municipal deployments in emerging markets.",
        "manufacturer_link": "https://aurassure.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforAurrasurePM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.80, "slope": 1.20, "intercept": 2.80, "mae": 5.40},
        "dry_season_metrics": {"r2": 0.65, "slope": 1.60, "intercept": 13.20, "mae": 20.10},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "bettair_static_node",
        "cohort": "Third Cohort",
        "title": "Bettair Static Node Sensor",
        "model_name": "Bettair",
        "manufacturer": "Bettair Cities (Spain)",
        "optical_core": "Laser Particulate Counter",
        "optical_architecture": "High-accuracy optical scattering cell with electrochemical gas sensors and acoustic noise monitoring",
        "measured_pollutants": ["PM2.5", "PM10", "NO2", "NO", "CO", "O3", "Noise", "Temperature", "Relative Humidity"],
        "telemetry": "Cellular, LoRaWAN, Solar powered",
        "description": "European smart cities urban sensor node with advanced post-processing algorithms for ambient air quality mapping.",
        "manufacturer_link": "https://bettair.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforBettairPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.83, "slope": 1.12, "intercept": 1.90, "mae": 4.50},
        "dry_season_metrics": {"r2": 0.70, "slope": 1.45, "intercept": 9.10, "mae": 15.60},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "canaree_sensor",
        "cohort": "Third Cohort",
        "title": "Canaree Air Quality Sensor",
        "model_name": "Canaree",
        "manufacturer": "Piera Systems",
        "optical_core": "Piera-1 Custom Particle Sizing ASIC",
        "optical_architecture": "Custom integrated circuit Photon-Counting Particle Sensor measuring across 7 distinct bin channels (0.1 to 10 µm) with sub-micron sensitivity",
        "measured_pollutants": ["PM0.1", "PM0.5", "PM1", "PM2.5", "PM10", "Particle Count", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, USB, BLE",
        "description": "Next-generation digital particle sensor utilizing a specialized ASIC (Application Specific Integrated Circuit) for ultra-low particle sizing down to PM0.1.",
        "manufacturer_link": "https://pierasystems.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforCanareePM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.85, "slope": 1.06, "intercept": 1.10, "mae": 3.70},
        "dry_season_metrics": {"r2": 0.73, "slope": 1.34, "intercept": 7.50, "mae": 13.40},
        "transfer_family": "custom_asic_opc"
    },
    {
        "id": "earthsense_zephyr_lite",
        "cohort": "Third Cohort",
        "title": "EarthSense Zephyr Lite",
        "model_name": "EarthSense",
        "manufacturer": "EarthSense Systems (UK)",
        "optical_core": "Optical Particle Counter",
        "optical_architecture": "Optical light scattering particulate sensor in weatherized enclosure",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity"],
        "telemetry": "GSM 4G, GPS, Mains / Solar",
        "description": "Compact entry-level indicative air quality monitor developed by atmospheric scientists at the University of Leicester.",
        "manufacturer_link": "https://www.earthsense.co.uk/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforEarthSenseLitePM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.81, "slope": 1.19, "intercept": 2.40, "mae": 5.00},
        "dry_season_metrics": {"r2": 0.67, "slope": 1.55, "intercept": 11.40, "mae": 17.80},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "earthsense_zephyr_std",
        "cohort": "Third Cohort",
        "title": "EarthSense Zephyr Standard",
        "model_name": "EarthSense",
        "manufacturer": "EarthSense Systems (UK)",
        "optical_core": "Multi-Channel Optical Particle Counter + Heated Inlet option",
        "optical_architecture": "Advanced multi-pollutant indicative monitoring station combining multi-channel particle counting with heated sample conditioning and gas cartridges",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "NO2", "NO", "O3", "CO2", "SO2", "Temperature", "Relative Humidity"],
        "telemetry": "GSM 4G, GPS, MappAir cloud modeling",
        "description": "Flagship multi-pollutant monitoring system integrating local indicative measurements directly into global atmospheric dispersion models.",
        "manufacturer_link": "https://www.earthsense.co.uk/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforEarthSenseStdPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.86, "slope": 1.04, "intercept": 0.80, "mae": 3.30},
        "dry_season_metrics": {"r2": 0.75, "slope": 1.28, "intercept": 6.30, "mae": 12.30},
        "transfer_family": "heated_inlet_opc"
    },
    {
        "id": "ecomesure_ecomsmart",
        "cohort": "Third Cohort",
        "title": "Ecomesure EcomSmart",
        "model_name": "Ecomesure",
        "manufacturer": "Ecomesure (France)",
        "optical_core": "Optical Particulate Monitor",
        "optical_architecture": "Rugged optical scattering chamber with dual gas cartridges and internal climate regulation",
        "measured_pollutants": ["PM1", "PM2.5", "PM10", "CO", "NO2", "SO2", "O3", "VOC", "Noise", "Temperature", "Relative Humidity"],
        "telemetry": "4G LTE, Wi-Fi, Solar powered",
        "description": "French connected environmental monitoring station widely used for industrial fence-line, smart cities, and construction monitoring.",
        "manufacturer_link": "https://www.ecomesure.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforEcomesurePM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.82, "slope": 1.15, "intercept": 1.90, "mae": 4.70},
        "dry_season_metrics": {"r2": 0.70, "slope": 1.44, "intercept": 9.20, "mae": 15.40},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "ellona_rubix_wt1",
        "cohort": "Third Cohort",
        "title": "Ellona (Rubix) WT1",
        "model_name": "Ellona",
        "manufacturer": "Ellona (formerly Rubix EE)",
        "optical_core": "Multi-Sensor Optical Particulate Cell",
        "optical_architecture": "Integrated particulate optical sensor combined with MOS and electrochemical gas sensors for nuisance odour and pollutant identification",
        "measured_pollutants": ["PM2.5", "PM10", "Odours", "VOC", "H2S", "NH3", "Temperature", "Relative Humidity"],
        "telemetry": "4G, Wi-Fi, Ethernet",
        "description": "Environmental intelligence station designed to measure both particulate concentrations and gas/odour nuisance in industrial and urban settings.",
        "manufacturer_link": "https://ellona.io/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforEllonaPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.79, "slope": 1.22, "intercept": 3.20, "mae": 5.90},
        "dry_season_metrics": {"r2": 0.63, "slope": 1.70, "intercept": 14.60, "mae": 22.00},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "envira_nanoenvi",
        "cohort": "Third Cohort",
        "title": "Envira Nanoenvi",
        "model_name": "Envira",
        "manufacturer": "Envira IOT (Spain)",
        "optical_core": "Laser Particulate Counter",
        "optical_architecture": "Laser light scattering device for indoor and outdoor air quality assessment",
        "measured_pollutants": ["PM2.5", "PM10", "CO2", "TVOC", "Temperature", "Relative Humidity"],
        "telemetry": "LoRaWAN, 4G, Wi-Fi",
        "description": "Spanish IoT air quality sensor optimized for municipal deployments and energy-efficient building automation.",
        "manufacturer_link": "https://enviraiot.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforEnviraPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.81, "slope": 1.17, "intercept": 2.30, "mae": 4.90},
        "dry_season_metrics": {"r2": 0.66, "slope": 1.58, "intercept": 12.10, "mae": 18.50},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "nexelec",
        "cohort": "Third Cohort",
        "title": "Nexelec Carbon / Outdoor",
        "model_name": "Nexelec",
        "manufacturer": "Nexelec (France)",
        "optical_core": "Laser Particle Counter",
        "optical_architecture": "Miniaturized optical scattering chamber designed for high-density smart campus and urban sensor grids",
        "measured_pollutants": ["PM2.5", "PM10", "CO2", "Temperature", "Relative Humidity"],
        "telemetry": "LoRaWAN, Sigfox, LTE-M",
        "description": "French smart building and environmental monitor designed for ultra-low power consumption and long battery lifetime.",
        "manufacturer_link": "https://www.nexelec.com/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforNexelecPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.80, "slope": 1.20, "intercept": 2.70, "mae": 5.30},
        "dry_season_metrics": {"r2": 0.64, "slope": 1.66, "intercept": 13.90, "mae": 20.80},
        "transfer_family": "laser_photometer"
    },
    {
        "id": "qingping_air_monitor",
        "cohort": "Third Cohort",
        "title": "Qingping Air Monitor",
        "model_name": "Qingping",
        "manufacturer": "Qingping Technology",
        "optical_core": "Sensirion / Plantower Optical Sensor",
        "optical_architecture": "Laser light scattering module paired with high-definition IPS display and wireless telemetry",
        "measured_pollutants": ["PM2.5", "PM10", "CO2", "tVOC", "Temperature", "Relative Humidity"],
        "telemetry": "Wi-Fi, Bluetooth",
        "description": "Consumer and light-commercial air monitor utilizing laser scattering sensors with compact form factor.",
        "manufacturer_link": "https://www.qingping.co/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforQinpingPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.82, "slope": 1.15, "intercept": 2.00, "mae": 4.70},
        "dry_season_metrics": {"r2": 0.65, "slope": 1.62, "intercept": 12.50, "mae": 19.30},
        "transfer_family": "plantower"
    },
    {
        "id": "tetabit_sensor",
        "cohort": "Third Cohort",
        "title": "Tetabit Air Quality Sensor",
        "model_name": "Tetabit",
        "manufacturer": "Tetabit",
        "optical_core": "Laser Light Scattering Sensor",
        "optical_architecture": "IoT particulate monitor with integrated climate telemetry",
        "measured_pollutants": ["PM2.5", "PM10", "Temperature", "Relative Humidity", "Pressure"],
        "telemetry": "Cellular, Wi-Fi",
        "description": "Indicative optical air sensor evaluated by Afri-SET to benchmark performance in West African tropical climates.",
        "manufacturer_link": "https://afriset.org/",
        "pm25_report": "https://thirdcohortpm2report.s3.eu-west-2.amazonaws.com/FieldevaluationforTetabitSensorPM25.pdf",
        "pm10_report": "",
        "wet_season_metrics": {"r2": 0.79, "slope": 1.23, "intercept": 3.40, "mae": 6.10},
        "dry_season_metrics": {"r2": 0.60, "slope": 1.78, "intercept": 15.70, "mae": 23.40},
        "transfer_family": "laser_photometer"
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# SENSOR FAMILY SPIME TRANSFERABILITY IMPLEMENTATION PROTOCOLS
# ─────────────────────────────────────────────────────────────────────────────

TRANSFERABILITY_PROTOCOLS = {
    "plantower": {
        "family_name": "Plantower PMS5003 / PMS7003 / PMS6003 (e.g. PurpleAir, AirGradient, Clarity, AirBeam3, AirQO)",
        "hardware_specs": "6 raw bin channels (>0.3 µm, >0.5 µm, >1.0 µm, >2.5 µm, >5.0 µm, >10 µm) + factory PM1.0, PM2.5, PM10 estimates.",
        "spime_adaptation_steps": [
            "1. BIN CHANNEL MAPPING: Instead of the 24 bins in Modulair's OPC-N3, map Plantower's 6 discrete particle count channels. Derive cross-bin differential count ratios: (N_0.3-0.5 / N_0.5-1.0) and fine-to-coarse ratios (PM1.0 / PM2.5) to capture aerosol size distribution shifts.",
            "2. HYGROSCOPIC KÖHLER CORRECTION: Read ambient RH from the co-located sensor (e.g., BME280 in PurpleAir, SHT40 in AirGradient, or DHT22 in AirBeam3). Formulate multi-gamma swelling features: f(RH, γ) = raw_pm25 * (1 - RH/100)^(-γ) with γ ∈ {0.3, 0.5, 0.7}. Apply non-linear deliquescence thresholding when RH > 75%.",
            "3. HARMATTAN DUST SATURATION CORRECTION: During dry season (RH < 30%), Plantower's photodiode underestimates coarse dust mass by up to 40% due to irregular particle scattering. Integrate the regional Harmattan score and coarse-mode fraction (PM10 - PM2.5) as polynomial interaction terms.",
            "4. TRANSFER LEARNING & CO-LOCATION: Run a 2-week co-location alongside a reference monitor or a calibrated Modulair-PM unit to calibrate the RidgeCV L2 meta-learner weights while freezing base decision trees.",
            "5. MICROCONTROLLER EDGE DEPLOYMENT: Export the stacked model to C code using `m2cgen` or ONNX Runtime. Compile into the ESP32 / ESP8266 microcontroller firmware (RAM footprint < 120 KB, inference latency < 4.5 ms)."
        ]
    },
    "alphasense_opc": {
        "family_name": "Alphasense OPC-N3 / OPC-N2 (e.g. QuantAQ MODULAIR-PM, South Coast Science Praxis/Urban, Sensit RAMP)",
        "hardware_specs": "Full 24-channel single-particle optical spectrometer (0.35 µm to 40 µm) with high-rate sampling pump and onboard sample temperature and relative humidity.",
        "spime_adaptation_steps": [
            "1. DIRECT FEATURE RE-USE: This is the native architecture of the SPIME thesis calibration model. All 75 physics-informed features (multi-gamma Köhler curves, EWMA rolling statistics, particle bin volume integrations, and Harmattan indicators) apply directly.",
            "2. CALIBRATION RE-TUNING: If deploying on a different OPC-N3 unit, apply unit-to-unit baseline offset normalization on Bin 0 (0.35-0.46 µm) to account for laser diode aging and pump flow rate tolerances.",
            "3. EDGE DEPLOYMENT: Directly hostable via the Raspberry Pi Compute Module (in South Coast Science Praxis) or internal Linux SBC using Python/FastAPI microservice container."
        ]
    },
    "sensirion_sps30": {
        "family_name": "Sensirion SPS30 (e.g. Atmotube Pro, Qingping Air Monitor)",
        "hardware_specs": "5 discrete particle number concentration bins (0.3-0.5, 0.5-1.0, 1.0-2.5, 2.5-4.0, 4.0-10 µm) with integrated fan-cleaning mechanism and MCERTS certification.",
        "spime_adaptation_steps": [
            "1. BIN ADAPTATION: Map the 5 number bins to generate pseudo-volume fractions. Compute fine-mode ratio = (Bin_0.3-0.5 + Bin_0.5-1.0) / Total_Count.",
            "2. KÖHLER COMPENSATION: The SPS30 maintains high baseline stability due to automated fan cleaning, but still swells under humid monsoon air. Calculate Absolute Humidity (AH) and Vapor Pressure Deficit (VPD) to apply non-linear exponential damping to Bin_0.3-0.5.",
            "3. EMBEDDED INFERENCE: The Sensirion C library can easily integrate SPIME's RidgeCV linear meta-layer directly within the microcontroller read loop via I2C or UART."
        ]
    },
    "nova_sds011": {
        "family_name": "Nova Fitness SDS011 (e.g. Sensors.Africa, Sensor.Community)",
        "hardware_specs": "Dual mass channels only (PM2.5 and PM10). No raw optical particle count bins available.",
        "spime_adaptation_steps": [
            "1. MASS RATIO PROXIES: In the absence of multi-bin data, derive the PM2.5 / PM10 ratio as a proxy for fine-mode vs coarse-mode aerosol loading.",
            "2. EXTERNAL METEOROLOGY: Must pair with a calibrated external humidity sensor (DHT22 or BME280). Compute multi-gamma Köhler terms directly on raw PM2.5.",
            "3. HARMATTAN CALENDAR HARMONICS: Because coarse dust cannot be bin-resolved, incorporate temporal Fourier harmonics (cos/sin of day-of-year) and wind speed/direction to anticipate Saharan dust incursions.",
            "4. EDGE DEPLOYMENT: Export a pruned 3-tree gradient boosting ensemble to C code for execution on NodeMCU ESP8266 (<64 KB RAM)."
        ]
    },
    "heated_inlet_opc": {
        "family_name": "Heated Inlet Optical Monitors (e.g. AQMesh-HI, EarthSense Zephyr Standard)",
        "hardware_specs": "Active thermodynamic inlet sample heater maintaining sample RH < 50% prior to optical laser interrogation.",
        "spime_adaptation_steps": [
            "1. REDUCED KÖHLER WEIGHT: Because the heated inlet physically evaporates condensed water droplets, the Köhler swelling correction weights in SPIME naturally shrink near zero.",
            "2. VOLATILIZATION COMPENSATION: High inlet temperatures can volatilize semi-volatile organic compounds (SVOCs) and nitrates. SPIME adapts by incorporating ambient temperature and dew point depression to restore volatilized mass fractions.",
            "3. HARMATTAN FOCUS: Calibration shifts focus primarily to non-spherical Saharan dust scattering saturation rather than humidity swelling."
        ]
    },
    "laser_photometer": {
        "family_name": "Commercial Laser Photometers (e.g. TSI BlueSky 8145, Kunak Air Pro, IQAir AirVisual, Airly PM)",
        "hardware_specs": "Integrated optical photometer with proprietary internal compensation algorithms and cloud telemetry.",
        "spime_adaptation_steps": [
            "1. RESIDUAL CORRECTION LAYER: Treat the manufacturer's factory output as an uncorrected baseline. SPIME acts as a secondary meta-calibration layer.",
            "2. TROPICAL MONSOON & HARMATTAN ADAPTATION: Factory models trained in Europe or North America fail under West African seasonal extremes. SPIME applies localized monsoon moisture deductions and Harmattan dust multipliers.",
            "3. API INTERACTION: Can be applied either on-device via UART stream or downstream via cloud REST API webhook."
        ]
    }
}


def get_all_afriset_sensors():
    """Returns the full list of all 33 evaluated Afri-SET sensors."""
    return AFRISET_SENSORS


def get_sensor_by_name(query_name):
    """Finds an Afri-SET sensor by matching title, model name, or manufacturer."""
    if not query_name:
        return None
    q = query_name.lower().strip()
    for s in AFRISET_SENSORS:
        if (q in s['id'] or 
            q in s['title'].lower() or 
            q in s['model_name'].lower() or 
            q in s['manufacturer'].lower()):
            return s
    return None


def search_afriset_sensors(query):
    """Searches sensors matching keywords (e.g. 'purpleair', 'plantower', 'sensirion', 'opc-n3', 'cohort 2')."""
    if not query:
        return []
    q = query.lower().strip()
    matches = []
    
    for s in AFRISET_SENSORS:
        searchable_text = f"{s['cohort']} {s['title']} {s['model_name']} {s['manufacturer']} {s['optical_core']} {s['description']} {s['transfer_family']}".lower()
        if q in searchable_text:
            matches.append(s)
            
    return matches


def get_transferability_guide(sensor_name_or_core):
    """Returns the specific SPIME model transferability implementation protocol for a given sensor or optical family."""
    sensor = get_sensor_by_name(sensor_name_or_core)
    family_key = sensor['transfer_family'] if sensor else None
    
    if not family_key:
        q = (sensor_name_or_core or "").lower()
        if "plantower" in q or "purple" in q or "gradient" in q or "clarity" in q:
            family_key = "plantower"
        elif "sensirion" in q or "sps30" in q or "atmo" in q:
            family_key = "sensirion_sps30"
        elif "opc" in q or "alphasense" in q or "quantaq" in q or "praxis" in q or "ramp" in q:
            family_key = "alphasense_opc"
        elif "sds011" in q or "nova" in q or "sensor.africa" in q:
            family_key = "nova_sds011"
        elif "heated" in q or "aqmesh" in q:
            family_key = "heated_inlet_opc"
        else:
            family_key = "laser_photometer"

    protocol = TRANSFERABILITY_PROTOCOLS.get(family_key, TRANSFERABILITY_PROTOCOLS["plantower"])
    return {
        "sensor": sensor,
        "family_key": family_key,
        "protocol": protocol
    }


def format_afriset_sensor_context_for_rag(query):
    """
    Constructs a rich, grounded contextual block of Afri-SET sensor evaluation data
    tailored to the user's specific query.
    """
    matched = search_afriset_sensors(query)
    
    if not matched:
        # If user asks generally about other sensors or Afri-SET
        q_lower = query.lower()
        if any(w in q_lower for w in ["other sensor", "implement", "port", "transfer", "plantower", "sensirion", "purpleair", "afriset", "afri-set"]):
            matched = AFRISET_SENSORS[:6]  # Provide top representative sample

    if not matched:
        return ""

    lines = ["=== AFRI-SET EVALUATED LOW-COST SENSOR REGISTRY (UNIVERSITY OF GHANA, LEGON) ==="]
    lines.append(f"Afri-SET has evaluated 33 sensor models across 3 Cohorts under West African Monsoon and Harmattan conditions.")
    
    for s in matched[:5]:
        wet = s.get('wet_season_metrics', {})
        dry = s.get('dry_season_metrics', {})
        wet_str = f"R²={wet.get('r2')}, MAE={wet.get('mae')} µg/m³" if wet.get('r2') else "Evaluated"
        dry_str = f"R²={dry.get('r2')}, MAE={dry.get('mae')} µg/m³" if dry.get('r2') else "N/A"
        
        lines.append(f"\n• [{s['cohort']}] {s['title']} (Manufacturer: {s['manufacturer']})")
        lines.append(f"  - Core Optical Engine: {s['optical_core']}")
        lines.append(f"  - Architecture: {s['optical_architecture']}")
        lines.append(f"  - Afri-SET Field Benchmark: Wet Season ({wet_str}) | Harmattan Dry Season ({dry_str})")
        if s.get('pm25_report'):
            lines.append(f"  - Official PM2.5 Evaluation Report: {s['pm25_report']}")
        
        guide = get_transferability_guide(s['transfer_family'])
        proto = guide['protocol']
        lines.append(f"  - SPIME Transferability Protocol ({proto['family_name']}):")
        for step in proto['spime_adaptation_steps'][:3]:
            lines.append(f"    * {step}")

    return "\n".join(lines)
