import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "airsense-modulair-pm-secret-2026")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/").strip()
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "airsense_db").strip()
    
    # Feature Mappings
    FEATURE_SETS = {
        14: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
            'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
            'vapor_pressure_deficit', 'dew_point_depression', 'rh_deliquescence_surge',
            'is_harmattan_month', 'harmattan_score', 'is_harmattan'
        ],
        11: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
            'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
            'is_harmattan_month', 'harmattan_score', 'is_harmattan'
        ],
        10: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week',
            'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
            'vapor_pressure_deficit', 'is_harmattan'
        ],
        8: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day',
            'rolling_mean_pm25', 'rolling_std_pm25', 'pm25_rh_interaction',
            'is_harmattan'
        ],
        6: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day',
            'rolling_mean_pm25', 'is_harmattan'
        ],
        5: [
            'pm25', 'sample_temp', 'sample_rh', 'hour_of_day', 'day_of_week'
        ]
    }

    DISTINCT_MODEL_CONFIG = {
        "stacked_physics_meta_ensemble": {
            "name": "🏆 SPIME v4 Ensemble",
            "file_names": ["stacked_physics_meta_ensemble.joblib"],
            "features": 75
        },
        "random_forest_pm25_model_update2": {
            "name": "Random Forest v2",
            "file_names": ["random_forest_pm25_model_update2.joblib", "random_forest_tuned.joblib"],
            "features": 11
        },
        "two_stage_purged_calibrator": {
            "name": "Two-Stage Purged Calibrator",
            "file_names": ["two_stage_purged_calibrator.joblib"],
            "features": 8
        },
        "pmc_hybrid_calibrator": {
            "name": "PMC Hybrid Calibrator",
            "file_names": ["pmc_hybrid_calibrator.joblib"],
            "features": 10
        },
        "moe_expert_model": {
            "name": "Atmospheric MoE",
            "file_names": ["moe_expert_model.joblib"],
            "features": 14
        },
        "compact_generalization_rf": {
            "name": "Compact Generalization RF",
            "file_names": ["compact_generalization_rf.joblib"],
            "features": 5
        }
    }
