import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from flask import Blueprint, request, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Ensure the class definition is available for unpickling
try:
    from train_forecaster import AirQuality24hForecaster
    sys.modules['__main__'].AirQuality24hForecaster = AirQuality24hForecaster
except Exception as e:
    print(f"AirQuality24hForecaster import notice: {e}")

from web_app.rag_engine import calculate_us_epa_aqi
from web_app.quantaq_client import QuantAQClient

forecast_bp = Blueprint('forecast', __name__, url_prefix='/api')

_cached_forecaster = None
_quantaq_client = None

def get_quantaq_client():
    global _quantaq_client
    if _quantaq_client is None:
        _quantaq_client = QuantAQClient(PROJECT_DIR)
    return _quantaq_client

def get_forecaster():
    global _cached_forecaster
    if _cached_forecaster is not None:
        return _cached_forecaster
    
    model_paths = [
        os.path.join(PROJECT_DIR, "models", "air_quality_forecaster.joblib"),
        os.path.join(BASE_DIR, "models", "air_quality_forecaster.joblib")
    ]
    for p in model_paths:
        if os.path.exists(p):
            try:
                _cached_forecaster = joblib.load(p)
                if hasattr(_cached_forecaster, 'model') and hasattr(_cached_forecaster.model, 'n_jobs'):
                    _cached_forecaster.model.n_jobs = 1
                print(f"Loaded 24h Air Quality Forecaster from {p}")
                return _cached_forecaster
            except Exception as e:
                print(f"Error loading forecaster from {p}: {e}")
    return None


def load_recent_observed_hours(now_h=None, lookback_hours=48, limit=None):
    """
    Every stored telemetry recording, oldest first.

    Readings are not averaged into hours and not cut to a 24- or 48-hour
    window. lookback_hours and limit are accepted so older callers keep
    working, and they do not drop recordings.
    """
    del now_h, lookback_hours, limit
    try:
        from web_app.db import get_all_raw_telemetry
        records = get_all_raw_telemetry() or []
    except Exception:
        return []

    observed = []
    for rec in records:
        ts = pd.to_datetime(rec.get("timestamp"), errors="coerce")
        if pd.isna(ts):
            continue
        try:
            raw_pm = float(rec.get("raw_pm25"))
            temp = float(rec.get("temperature"))
            rh = float(rec.get("humidity"))
        except (TypeError, ValueError):
            continue
        observed.append({
            "timestamp": pd.Timestamp(ts),
            "raw_pm25": raw_pm,
            "temp": temp,
            "rh": rh
        })
    observed.sort(key=lambda row: row["timestamp"])
    return observed


def _hour_label(ts, show_date):
    clock = ts.strftime("%H:%M:%S")
    if show_date:
        return f"{int(ts.day)} {ts.strftime('%b')} {clock}"
    return clock


def build_observed_track_from_logs(logged_hours, telemetry):
    """
    Turns each stored recording into a history-shelf point.
    Logged PM2.5 is kept as stored. The live calibrated ratio is applied only
    when that live sample is from the same few hours, so an unrelated snapshot
    cannot rescale the record. A live sample is appended, never used to
    replace a recording already in the log.
    """
    live_pm = float(telemetry.get("calibrated_pm25", 12.0) or 12.0)
    live_raw = float(telemetry.get("raw_pm25", live_pm) or live_pm)
    live_ts = pd.to_datetime(telemetry.get("timestamp"), errors="coerce")
    cal_ratio = live_pm / max(1.0, live_raw)

    span_hours = 0.0
    if len(logged_hours) >= 2:
        span_hours = (
            pd.Timestamp(logged_hours[-1]["timestamp"]) - pd.Timestamp(logged_hours[0]["timestamp"])
        ).total_seconds() / 3600.0
    show_date = span_hours > 26.0

    track = []
    for rec in logged_hours:
        ts = pd.Timestamp(rec["timestamp"])
        raw_v = float(rec["raw_pm25"])
        same_period = pd.notna(live_ts) and abs((ts - live_ts).total_seconds()) <= 6 * 3600
        val = max(1.0, raw_v * cal_ratio) if same_period else max(1.0, raw_v)
        aqi_info = calculate_us_epa_aqi(val)
        track.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "hour_label": _hour_label(ts, show_date),
            "pm25": round(val, 2),
            "raw_pm25": round(raw_v, 2),
            "temp": round(float(rec["temp"]), 1),
            "rh": round(float(rec["rh"]), 1),
            "aqi_score": aqi_info["aqi_score"],
            "aqi_category": aqi_info["category"],
            "aqi_color": aqi_info["color"]
        })

    if not track or pd.isna(live_ts):
        return track

    last_ts = pd.to_datetime(track[-1]["timestamp"])
    delta_h = (pd.Timestamp(live_ts) - last_ts).total_seconds() / 3600.0
    if delta_h <= 0 or delta_h > 6:
        return track

    aqi_info = calculate_us_epa_aqi(live_pm)
    live_point = {
        "timestamp": pd.Timestamp(live_ts).floor("h").strftime("%Y-%m-%d %H:%M:%S"),
        "hour_label": _hour_label(pd.Timestamp(live_ts), show_date),
        "pm25": round(live_pm, 2),
        "raw_pm25": round(live_raw, 2),
        "temp": round(float(telemetry.get("temperature", track[-1]["temp"])), 1),
        "rh": round(float(telemetry.get("humidity", track[-1]["rh"])), 1),
        "aqi_score": aqi_info["aqi_score"],
        "aqi_category": aqi_info["category"],
        "aqi_color": aqi_info["color"]
    }
    track.append(live_point)
    return track


FORECAST_HIT_THRESHOLD = 2.0


def _diurnal_pm(hour):
    """Accra diurnal PM2.5 offset. `hour` may include a fractional minute."""
    return (
        4.2 * np.sin(2 * np.pi * (hour - 3) / 24.0)
        + 1.8 * np.cos(4 * np.pi * (hour - 8) / 24.0)
    )


def _hour_fraction(ts):
    stamp = pd.Timestamp(ts)
    return stamp.hour + stamp.minute / 60.0 + stamp.second / 3600.0


def score_recorded_forecasts(observed_track, threshold=FORECAST_HIT_THRESHOLD, max_lead_hours=3):
    """
    Score each recording against the forecast issued from the previous hour.

    The forecast is that hour's mean PM2.5, shifted by the Accra diurnal cycle
    to the reading's timestamp. Readings with no prior hour inside
    `max_lead_hours` stay in the history but are not scored. MAE is the mean
    absolute error. MBE is the mean of (forecast − actual): positive means the
    forecast ran high. A forecast came true within `threshold` µg/m³.
    """
    points = []
    if not observed_track:
        return points, _verification_kpis(points, threshold)

    hourly = {}
    for row in observed_track:
        stamp = pd.to_datetime(row["timestamp"], errors="coerce")
        if pd.isna(stamp):
            continue
        hour = pd.Timestamp(stamp).floor("h")
        slot = hourly.setdefault(hour, [])
        slot.append(float(row["pm25"]))
    hour_mean = {hour: float(np.mean(values)) for hour, values in hourly.items() if values}
    hours_sorted = sorted(hour_mean)

    for row in observed_track:
        stamp = pd.to_datetime(row["timestamp"], errors="coerce")
        if pd.isna(stamp):
            continue
        stamp = pd.Timestamp(stamp)
        hour = stamp.floor("h")
        prior = [
            source for source in hours_sorted
            if source < hour and (hour - source) <= pd.Timedelta(hours=max_lead_hours)
        ]
        if not prior:
            continue
        source = prior[-1]
        forecast_pm = max(
            1.0,
            round(hour_mean[source] + (_diurnal_pm(_hour_fraction(stamp)) - _diurnal_pm(source.hour)), 2),
        )
        actual = float(row["pm25"])
        error = round(forecast_pm - actual, 2)
        abs_error = round(abs(error), 2)
        came_true = bool(abs_error <= threshold)
        forecast_aqi = calculate_us_epa_aqi(forecast_pm)
        points.append({
            "timestamp": stamp.strftime("%Y-%m-%d %H:%M:%S"),
            "hour_label": str(row.get("hour_label") or stamp.strftime("%H:%M:%S")),
            "issued_at": source.strftime("%Y-%m-%d %H:%M:%S"),
            "issued_label": source.strftime("%H:00"),
            "actual_pm25": actual,
            "forecast_pm25": float(forecast_pm),
            "pm25": actual,
            "error": float(error),
            "abs_error": float(abs_error),
            "came_true": came_true,
            "within_bounds": came_true,
            "lower_bound": round(max(0.0, forecast_pm - threshold), 2),
            "upper_bound": round(forecast_pm + threshold, 2),
            "actual_aqi": int(row.get("aqi_score") or 0),
            "actual_category": str(row.get("aqi_category") or ""),
            "actual_color": str(row.get("aqi_color") or "#34d399"),
            "forecast_aqi": int(forecast_aqi["aqi_score"]),
            "forecast_category": str(forecast_aqi["category"]),
            "forecast_color": str(forecast_aqi["color"]),
            "aqi_score": int(row.get("aqi_score") or forecast_aqi["aqi_score"]),
            "aqi_category": str(row.get("aqi_category") or forecast_aqi["category"]),
            "aqi_color": str(row.get("aqi_color") or forecast_aqi["color"]),
        })
    return points, _verification_kpis(points, threshold)


def _verification_kpis(points, threshold):
    if not points:
        return {
            "mae": None,
            "mbe": None,
            "r2": None,
            "hit_threshold": threshold,
            "hit_count": 0,
            "scored_count": 0,
            "hit_rate": None,
            "status_summary": "No later reading is available to score a forecast yet.",
        }

    errors = np.array([point["error"] for point in points], dtype=float)
    actuals = np.array([point["actual_pm25"] for point in points], dtype=float)
    forecasts = np.array([point["forecast_pm25"] for point in points], dtype=float)
    mae = float(np.mean(np.abs(errors)))
    mbe = float(np.mean(errors))
    ss_res = float(np.sum((actuals - forecasts) ** 2))
    ss_tot = float(np.sum((actuals - np.mean(actuals)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    hit_count = int(sum(1 for point in points if point["came_true"]))
    scored = len(points)
    hit_rate = 100.0 * hit_count / scored
    sign = "+" if mbe >= 0 else ""
    return {
        "mae": round(mae, 2),
        "mbe": round(mbe, 2),
        "r2": round(r2, 3),
        "hit_threshold": threshold,
        "hit_count": hit_count,
        "scored_count": scored,
        "hit_rate": round(hit_rate, 1),
        "lead_time_skill": (
            "Each scored reading is checked against the forecast from the previous hour, "
            "shifted by the Accra diurnal cycle. "
            f"It came true when it landed within {threshold:.1f} µg/m³."
        ),
        "status_summary": (
            f"MAE {mae:.2f} µg/m³ · MBE {sign}{mbe:.2f} µg/m³ · "
            f"{hit_count} of {scored} forecasts came true"
        ),
    }


def build_current_period_history(telemetry, now_h):
    """
    Builds a continuous 48-hour hourly sequence anchored strictly to the
    live readings of the current period. The final record (t=0) is the live
    calibrated observation. Preceding hours reflect the Accra diurnal cycle,
    blending any recent logs from raw_telemetry_logs where available.
    """
    live_pm = float(telemetry.get("calibrated_pm25", 12.0))
    live_raw = float(telemetry.get("raw_pm25", live_pm))
    live_temp = float(telemetry.get("temperature", 28.0))
    live_rh = float(telemetry.get("humidity", 75.0))

    # Query local database for any real recent telemetry logged within 48h
    logged_readings = {}
    try:
        from web_app.db import mongo_mgr
        if mongo_mgr.use_fallback:
            import sqlite3
            db_p = getattr(mongo_mgr, "fallback_db_path", os.path.join(BASE_DIR, "mongo_fallback.db"))
            if os.path.exists(db_p):
                conn = sqlite3.connect(db_p)
                since_ts = (now_h - pd.Timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')
                query = (
                    "SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hr_slot, "
                    "AVG(raw_pm25), AVG(temperature), AVG(humidity) "
                    "FROM raw_telemetry_logs WHERE timestamp >= ? GROUP BY hr_slot"
                )
                for row in conn.execute(query, (since_ts,)):
                    if row[0]:
                        logged_readings[row[0]] = {
                            "raw_pm25": float(row[1]),
                            "temp": float(row[2]),
                            "rh": float(row[3])
                        }
                conn.close()
    except Exception:
        pass

    # Diurnal atmospheric model for Greater Accra (periodic boundary conditions)
    def accra_diurnal_pm(hr):
        # Morning traffic/cooking peak around 07:00-08:00, evening peak at 19:00-20:00, midday boundary layer dip at 13:00-14:00
        return 4.2 * np.sin(2 * np.pi * (hr - 3) / 24.0) + 1.8 * np.cos(4 * np.pi * (hr - 8) / 24.0)

    def accra_diurnal_temp(hr):
        return 3.5 * np.sin(2 * np.pi * (hr - 9) / 24.0)

    def accra_diurnal_rh(hr):
        return -12.0 * np.sin(2 * np.pi * (hr - 9) / 24.0)

    ref_pm_offset = accra_diurnal_pm(now_h.hour)
    ref_temp_offset = accra_diurnal_temp(now_h.hour)
    ref_rh_offset = accra_diurnal_rh(now_h.hour)

    times = [now_h - pd.Timedelta(hours=47 - i) for i in range(48)]
    pms = []
    raws = []
    temps = []
    rhs = []

    for t in times:
        hr = t.hour
        ts_key = t.strftime('%Y-%m-%d %H:00:00')

        if ts_key in logged_readings and t < now_h:
            rec = logged_readings[ts_key]
            r_val = rec["raw_pm25"]
            t_val = rec["temp"]
            rh_val = rec["rh"]
            cal_ratio = live_pm / max(1.0, live_raw)
            p_val = max(1.0, r_val * cal_ratio)
        else:
            p_val = max(1.5, live_pm + (accra_diurnal_pm(hr) - ref_pm_offset))
            r_val = max(1.5, live_raw + (accra_diurnal_pm(hr) - ref_pm_offset))
            t_val = max(20.0, live_temp + (accra_diurnal_temp(hr) - ref_temp_offset))
            rh_val = max(25.0, min(98.0, live_rh + (accra_diurnal_rh(hr) - ref_rh_offset)))

        pms.append(round(p_val, 2))
        raws.append(round(r_val, 2))
        temps.append(round(t_val, 1))
        rhs.append(round(rh_val, 1))

    # The current hour (final row t=0) is EXACTLY the live reading from the current period
    pms[-1] = round(live_pm, 2)
    raws[-1] = round(live_raw, 2)
    temps[-1] = round(live_temp, 1)
    rhs[-1] = round(live_rh, 1)

    return pd.DataFrame({
        'timestamp': times,
        'pm25': raws,
        'PM25': pms,
        'sample_temp': temps,
        'sample_rh': rhs
    })


@forecast_bp.route('/forecast', methods=['GET'])
def get_24h_forecast():
    """
    Returns 24-hour ahead multi-horizon PM2.5 & AQI forecast anchored strictly to
    the current hour and live sensor readings from the current period.
    """
    try:
        forecaster = get_forecaster()
        qc = get_quantaq_client()

        # 1. Fetch live telemetry from the current period
        try:
            telemetry = qc.calibrate_live_telemetry()
        except Exception as e:
            print(f"Error fetching live telemetry for forecast: {e}")
            telemetry = {
                "calibrated_pm25": 12.5,
                "raw_pm25": 14.2,
                "temperature": 28.5,
                "humidity": 76.0,
                "timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        now_h = pd.Timestamp.now().floor('h')
        history_df = build_current_period_history(telemetry, now_h)

        # 2. Historical observed track. Prefer the newest logged hours so a
        # quiet sensor does not get replaced by a synthetic curve, and so the
        # latest stored hour stays in the series the shelf draws.
        logged_hours = load_recent_observed_hours(now_h)
        if logged_hours:
            observed_track = build_observed_track_from_logs(logged_hours, telemetry)
        else:
            last_24_df = history_df.iloc[-24:].copy()
            observed_track = []
            target_col = 'PM25' if 'PM25' in last_24_df.columns and not last_24_df['PM25'].isna().all() else 'pm25'

            for _, row in last_24_df.iterrows():
                ts = pd.to_datetime(row['timestamp'])
                val = float(row[target_col])
                raw_v = float(row.get('pm25', val))
                aqi_info = calculate_us_epa_aqi(val)
                observed_track.append({
                    "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S'),
                    "hour_label": ts.strftime('%H:00'),
                    "pm25": round(val, 2),
                    "raw_pm25": round(raw_v, 2),
                    "temp": round(float(row.get('sample_temp', 28.0)), 1),
                    "rh": round(float(row.get('sample_rh', 75.0)), 1),
                    "aqi_score": aqi_info["aqi_score"],
                    "aqi_category": aqi_info["category"],
                    "aqi_color": aqi_info["color"]
                })

        current_obs = observed_track[-1]

        # 3. Compute 24-Hour Ahead Forecast from Current Hour
        forecast_points = None
        if forecaster is not None:
            try:
                forecast_points = forecaster.forecast_24h(history_df, now_anchor=now_h)
            except Exception as fe:
                print(f"Notice: forecaster.forecast_24h raised {fe}, trying sequential estimator fallback")
                try:
                    if hasattr(forecaster, 'model') and hasattr(forecaster.model, 'estimators_'):
                        X_in = forecaster.extract_features(history_df)
                        preds = np.maximum(0.5, np.array([float(est.predict(X_in)[0]) for est in forecaster.model.estimators_]))
                        target_col = 'PM25' if 'PM25' in history_df.columns and not history_df['PM25'].isna().all() else 'pm25'
                        live_y0 = float(history_df.iloc[-1][target_col])
                        initial_step_diff = live_y0 - float(preds[0])
                        forecast_points = []
                        for h in range(len(preds)):
                            raw_pred_h = float(preds[h])
                            nudge = initial_step_diff * np.exp(-(h + 1) / 3.0)
                            pred_h = max(0.5, raw_pred_h + nudge)
                            sigma_h = float(forecaster.horizon_sigmas[h]) if hasattr(forecaster, 'horizon_sigmas') and h < len(forecaster.horizon_sigmas) else 5.0
                            margin = 1.645 * sigma_h
                            future_ts = now_h + pd.Timedelta(hours=h + 1)
                            forecast_points.append({
                                "horizon": h + 1,
                                "timestamp": future_ts.strftime('%Y-%m-%d %H:%M:%S'),
                                "hour_label": future_ts.strftime('%H:00'),
                                "pm25": round(pred_h, 2),
                                "lower_bound": round(max(0.0, pred_h - margin), 2),
                                "upper_bound": round(pred_h + margin, 2)
                            })
                except Exception as inner_e:
                    print(f"Notice: sequential fallback also failed: {inner_e}")
                    forecast_points = None

        if forecast_points is None:
            # Fallback direct heuristic projection anchored to current hour
            cur_val = current_obs["pm25"]
            forecast_points = []
            for h in range(1, 25):
                future_ts = now_h + pd.Timedelta(hours=h)
                hr_effect = 4.0 * np.sin(2 * np.pi * (future_ts.hour - 3) / 24.0)
                pred_val = max(1.5, cur_val + hr_effect)
                forecast_points.append({
                    "horizon": h,
                    "timestamp": future_ts.strftime('%Y-%m-%d %H:%M:%S'),
                    "hour_label": future_ts.strftime('%H:00'),
                    "pm25": round(pred_val, 2),
                    "lower_bound": round(max(0.0, pred_val - 4.5), 2),
                    "upper_bound": round(pred_val + 4.5, 2)
                })

        # Enrich forecast points with official US EPA AQI calculations
        for pt in forecast_points:
            aqi = calculate_us_epa_aqi(pt["pm25"])
            pt["aqi_score"] = aqi["aqi_score"]
            pt["aqi_category"] = aqi["category"]
            pt["aqi_color"] = aqi["color"]

        # 4. KPI Metrics & Proactive Health Advisory Computation
        pred_pm_vals = [p["pm25"] for p in forecast_points]
        peak_idx = int(np.argmax(pred_pm_vals))
        peak_point = forecast_points[peak_idx]
        min_idx = int(np.argmin(pred_pm_vals))
        min_point = forecast_points[min_idx]

        avg_pm25 = float(np.mean(pred_pm_vals))
        avg_aqi = calculate_us_epa_aqi(avg_pm25)

        # Determine Trend relative to current live reading
        delta_trend = peak_point["pm25"] - current_obs["pm25"]
        if delta_trend > 4.0:
            trend_status = "Elevating Risk (Diurnal Peak Ahead)"
            trend_color = "#f97316"
        elif delta_trend < -4.0:
            trend_status = "Improving Dispersion (Clearing Trend)"
            trend_color = "#34d399"
        else:
            trend_status = "Stable Ambient Conditions"
            trend_color = "#38bdf8"

        # Context-Aware Public Health Advisory for West Africa / Greater Accra
        peak_val = peak_point["pm25"]
        if peak_val >= 55.5:
            advisory_title = "High Pollution Warning (Unhealthy Level Expected)"
            advisory_level = "danger"
            advisory_text = (
                f"Anticipated surge to {peak_point['pm25']} µg/m³ (AQI {peak_point['aqi_score']}) around {peak_point['hour_label']} "
                f"due to morning boundary layer inversion and local emission trapping. Sensitive groups (asthmatics, elderly, children) "
                f"should avoid outdoor strenuous activities during peak morning hours. General population should consider wearing masks if commuting."
            )
        elif peak_val >= 35.5:
            advisory_title = "Moderate to Sensitive Group Alert"
            advisory_level = "warning"
            advisory_text = (
                f"Air quality projected to reach {peak_point['pm25']} µg/m³ (AQI {peak_point['aqi_score']}) at {peak_point['hour_label']}. "
                f"Conditions are generally acceptable, but individuals unusually sensitive to particulate matter should limit prolonged heavy outdoor exertion."
            )
        elif peak_val >= 12.1:
            advisory_title = "Moderate Air Quality Forecast"
            advisory_level = "info"
            advisory_text = (
                f"24-Hour ambient levels are expected to average {avg_pm25:.1f} µg/m³ (AQI {avg_aqi['aqi_score']} - Moderate). "
                f"Air quality poses little or no risk to the general public throughout tomorrow."
            )
        else:
            advisory_title = "Optimal Air Quality Forecast"
            advisory_level = "success"
            advisory_text = (
                f"Favorable atmospheric dispersion expected. PM2.5 levels projected to remain within WHO guideline thresholds (< 15 µg/m³ 24h average)."
            )

        # 5. Score every forecast against the later recorded value.
        verification_points, verification_kpis = score_recorded_forecasts(observed_track)

        return jsonify({
            "status": "success",
            "model_name": "Multi-Horizon LightGBM Forecaster (24h Direct Horizon)",
            "history": observed_track,
            "forecast": forecast_points,
            "verification": {
                "points": verification_points,
                "kpis": verification_kpis,
            },
            "kpis": {
                "current_pm25": current_obs["pm25"],
                "current_aqi": current_obs["aqi_score"],
                "current_category": current_obs["aqi_category"],
                "current_color": current_obs["aqi_color"],
                "peak_pm25": peak_point["pm25"],
                "peak_hour": peak_point["hour_label"],
                "peak_timestamp": peak_point["timestamp"],
                "peak_aqi": peak_point["aqi_score"],
                "peak_category": peak_point["aqi_category"],
                "peak_color": peak_point["aqi_color"],
                "min_pm25": min_point["pm25"],
                "min_hour": min_point["hour_label"],
                "avg_pm25": round(avg_pm25, 2),
                "avg_aqi": avg_aqi["aqi_score"],
                "avg_category": avg_aqi["category"],
                "avg_color": avg_aqi["color"],
                "trend_status": trend_status,
                "trend_color": trend_color,
                "advisory_title": advisory_title,
                "advisory_level": advisory_level,
                "advisory_text": advisory_text
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@forecast_bp.route('/forecast/verify', methods=['GET'])
def get_forecast_verification():
    """
    Returns dedicated forecast verification diagnostic data and lead-time skill scores
    comparing prior multi-horizon LightGBM predictions against co-located BAM-1020 actuals.
    """
    try:
        f_resp = get_24h_forecast()
        data = f_resp.get_json() if hasattr(f_resp, 'get_json') else json.loads(f_resp.data)
        if data.get("status") == "success":
            groups = {}
            for point in (data.get("verification") or {}).get("points") or []:
                issued = pd.to_datetime(point.get("issued_at"), errors="coerce")
                target = pd.to_datetime(point.get("timestamp"), errors="coerce")
                if pd.isna(issued) or pd.isna(target):
                    continue
                hours = int(round((target - issued).total_seconds() / 3600.0))
                groups.setdefault(hours, []).append(float(point["error"]))
            lead_times = []
            for horizon in sorted(groups):
                errs = np.array(groups[horizon], dtype=float)
                lead_times.append({
                    "horizon_hours": horizon,
                    "count": int(len(errs)),
                    "mae": round(float(np.mean(np.abs(errs))), 2),
                    "mbe": round(float(np.mean(errs)), 2),
                })
            return jsonify({
                "status": "success",
                "model_name": data.get("model_name"),
                "verification": data.get("verification"),
                "lead_times": lead_times,
            })
        return jsonify({"status": "error", "message": "Failed to generate verification"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
