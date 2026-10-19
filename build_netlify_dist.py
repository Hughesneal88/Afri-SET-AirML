"""
Build script to generate a production-ready static distribution for Netlify deployment.
Exports:
  - dist/index.html (Version 2 Studio)
  - dist/plot.html and dist/plot/index.html (Standalone Plotly View)
  - dist/v2.css
  - dist/v2.js (with offline fallback handlers)
  - dist/data/ (pre-computed models registry, telemetry snapshots, and prediction datasets)
  - dist/_redirects and netlify.toml (clean URLs and optional API proxy rules)
"""

import os
import shutil
import json
import urllib.request
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
DATA_DIR = os.path.join(DIST_DIR, 'data')

def write_forecast_snapshot(data_dir):
    """
    Write dist/data/forecast.json from the newest logged sensor hours.
    Netlify has no Flask process, and /api/forecast is what the history shelf reads.
    """
    try:
        import sys
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        import pandas as pd
        from web_app.blueprints.forecast import (
            load_recent_observed_hours,
            build_observed_track_from_logs,
            score_recorded_forecasts,
        )
        from web_app.rag_engine import calculate_us_epa_aqi

        telemetry_path = os.path.join(data_dir, "telemetry.json")
        telemetry = {
            "calibrated_pm25": 17.38,
            "raw_pm25": 18.51,
            "temperature": 32.2,
            "humidity": 63.3,
            "timestamp": "2026-10-03 01:44:36",
        }
        if os.path.exists(telemetry_path):
            with open(telemetry_path, "r", encoding="utf-8") as handle:
                cached = json.load(handle)
            telemetry = cached.get("telemetry") or cached

        now_h = pd.Timestamp.now().floor("h")
        logged_hours = load_recent_observed_hours(now_h)
        if not logged_hours:
            print("    [-] No logged telemetry hours available for history snapshot")
            return

        history = build_observed_track_from_logs(logged_hours, telemetry)
        if not history:
            print("    [-] Observed history track was empty")
            return

        last = history[-1]
        live_pm = float(last["pm25"])
        ref_hour = pd.to_datetime(last["timestamp"]).hour

        def diurnal(hour):
            import math
            return 4.2 * math.sin(2 * math.pi * (hour - 3) / 24.0) + 1.8 * math.cos(4 * math.pi * (hour - 8) / 24.0)

        ref = diurnal(ref_hour)
        anchor = pd.to_datetime(last["timestamp"]).floor("h")
        forecast = []
        for horizon in range(1, 25):
            future = anchor + pd.Timedelta(hours=horizon)
            pred = max(1.5, live_pm + (diurnal(future.hour) - ref))
            aqi = calculate_us_epa_aqi(pred)
            forecast.append({
                "horizon": horizon,
                "timestamp": future.strftime("%Y-%m-%d %H:%M:%S"),
                "hour_label": future.strftime("%H:00"),
                "pm25": round(pred, 2),
                "lower_bound": round(max(0.0, pred - 4.5), 2),
                "upper_bound": round(pred + 4.5, 2),
                "aqi_score": aqi["aqi_score"],
                "aqi_category": aqi["category"],
                "aqi_color": aqi["color"],
            })

        peak = max(forecast, key=lambda point: point["pm25"])
        verification_points, verification_kpis = score_recorded_forecasts(history)
        payload = {
            "status": "success",
            "model_name": "Observed Modulair-PM history",
            "history": history,
            "forecast": forecast,
            "verification": {
                "points": verification_points,
                "kpis": verification_kpis,
            },
            "kpis": {
                "current_pm25": last["pm25"],
                "current_aqi": last["aqi_score"],
                "current_category": last["aqi_category"],
                "peak_pm25": peak["pm25"],
                "peak_hour": peak["hour_label"],
                "peak_category": peak["aqi_category"],
                "peak_color": peak["aqi_color"],
            },
        }
        out_path = os.path.join(data_dir, "forecast.json")
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        print(
            f"    [+] Cached data/forecast.json ({len(history)} hours, "
            f"{verification_kpis.get('scored_count', 0)} scored, "
            f"MAE {verification_kpis.get('mae')} · MBE {verification_kpis.get('mbe')})"
        )
    except Exception as exc:
        print(f"    [-] Could not cache forecast history: {exc}")


def build():
    print(f"[*] Building Netlify distribution into: {DIST_DIR}")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, 'plot'), exist_ok=True)

    # 1. Process v2.html -> dist/index.html
    v2_template_path = os.path.join(BASE_DIR, 'web_app', 'templates', 'v2.html')
    with open(v2_template_path, 'r', encoding='utf-8') as f:
        v2_html = f.read()

    # Replace Flask url_for calls with direct static asset names
    v2_html = re.sub(r"\{\{\s*url_for\('static',\s*filename='v2\.css'\)\s*\}\}", "v2.css", v2_html)
    v2_html = re.sub(r"\{\{\s*url_for\('static',\s*filename='v2\.js'\)\s*\}\}", "v2.js", v2_html)
    
    with open(os.path.join(DIST_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(v2_html)
    print("  [+] Generated dist/index.html")

    # 2. Process plot_standalone.html -> dist/plot.html & dist/plot/index.html
    plot_template_path = os.path.join(BASE_DIR, 'web_app', 'templates', 'plot_standalone.html')
    with open(plot_template_path, 'r', encoding='utf-8') as f:
        plot_html = f.read()

    plot_html = plot_html.replace(
        "const res = await fetch(`/api/predict?model_key=${modelKey}&split=${split}&max_points=${maxPoints}`);",
        """let res = await fetch(`/api/predict?model_key=${modelKey}&split=${split}&max_points=${maxPoints}`);
            if (!res.ok) {
                res = await fetch(`/data/predict_${modelKey}_${split}.json`);
            }"""
    )
    plot_html = plot_html.replace(
        "const res = await fetch('/api/models');",
        """let res = await fetch('/api/models');
            if (!res.ok) {
                res = await fetch('/data/models.json');
            }"""
    )

    with open(os.path.join(DIST_DIR, 'plot.html'), 'w', encoding='utf-8') as f:
        f.write(plot_html)
    with open(os.path.join(DIST_DIR, 'plot', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(plot_html)
    print("  [+] Generated dist/plot.html and dist/plot/index.html with static data fallbacks")

    # 3. Copy v2.css
    shutil.copy2(
        os.path.join(BASE_DIR, 'web_app', 'static', 'v2.css'),
        os.path.join(DIST_DIR, 'v2.css')
    )
    print("  [+] Copied dist/v2.css")

    history_template = os.path.join(BASE_DIR, 'web_app', 'templates', 'history.html')
    if os.path.exists(history_template):
        shutil.copy2(history_template, os.path.join(DIST_DIR, 'history.html'))
        print("  [+] Copied dist/history.html")

    # 4. Enhance and copy v2.js with fallback data routing
    v2_js_path = os.path.join(BASE_DIR, 'web_app', 'static', 'v2.js')
    with open(v2_js_path, 'r', encoding='utf-8') as f:
        v2_js = f.read()

    # In v2.js, update fetch('/api/predict...') to fall back to static data if needed
    v2_js_enhanced = v2_js.replace(
        "const res = await fetch(`/api/predict?model_key=${modelKey}&split=${split}&max_points=500`);",
        """let res = await fetch(`/api/predict?model_key=${modelKey}&split=${split}&max_points=500`);
            if (!res.ok) {
                res = await fetch(`/data/predict_${modelKey}_${split}.json`);
            }"""
    )

    # In v2.js, update fetch('/api/models') to fall back to /data/models.json
    v2_js_enhanced = v2_js_enhanced.replace(
        "const res = await fetch('/api/models');",
        """let res = await fetch('/api/models');
            if (!res.ok) {
                res = await fetch('/data/models.json');
            }"""
    )

    # In v2.js, update fetch('/api/live_telemetry...') to fall back to /data/telemetry.json
    v2_js_enhanced = v2_js_enhanced.replace(
        "const res = await fetch('/api/live_telemetry?model_key=stacked_physics_meta_ensemble');",
        """let res = await fetch('/api/live_telemetry?model_key=stacked_physics_meta_ensemble');
            if (!res.ok) {
                res = await fetch('/data/telemetry.json');
            }"""
    )

    # History and forecast share /api/forecast. On Netlify that route is the static snapshot.
    v2_js_enhanced = v2_js_enhanced.replace(
        "const res = await fetch('/api/forecast');",
        """let res = await fetch('/api/forecast');
            if (!res.ok) {
                res = await fetch('/data/forecast.json');
            }"""
    )

    with open(os.path.join(DIST_DIR, 'v2.js'), 'w', encoding='utf-8') as f:
        f.write(v2_js_enhanced)
    print("  [+] Generated dist/v2.js with offline fallbacks")

    # 5. Fetch and cache static datasets from live local Flask server
    print("  [*] Fetching pre-computed datasets from local server (http://127.0.0.1:5000)...")
    try:
        # Cache /api/models
        req = urllib.request.urlopen("http://127.0.0.1:5000/api/models")
        models_data = json.loads(req.read().decode('utf-8'))
        with open(os.path.join(DATA_DIR, 'models.json'), 'w', encoding='utf-8') as f:
            json.dump(models_data, f, indent=2)
        print("    [+] Cached data/models.json")
    except Exception as e:
        print(f"    [-] Could not cache models: {e}")

    try:
        # Cache /api/live_telemetry
        req = urllib.request.urlopen("http://127.0.0.1:5000/api/live_telemetry?model_key=stacked_physics_meta_ensemble")
        telemetry_data = json.loads(req.read().decode('utf-8'))
        with open(os.path.join(DATA_DIR, 'telemetry.json'), 'w', encoding='utf-8') as f:
            json.dump(telemetry_data, f, indent=2)
        print("    [+] Cached data/telemetry.json")
    except Exception as e:
        print(f"    [-] Could not cache telemetry: {e}")

    write_forecast_snapshot(DATA_DIR)

    # Cache predictions for all models and splits
    models_to_cache = [
        'stacked_physics_meta_ensemble',
        'random_forest_pm25_model_update2',
        'two_stage_purged_calibrator',
        'pmc_hybrid_calibrator',
        'moe_expert_model',
        'compact_generalization_rf'
    ]
    splits_to_cache = ['val', 'test', 'all']

    for m in models_to_cache:
        for s in splits_to_cache:
            out_file = os.path.join(DATA_DIR, f"predict_{m}_{s}.json")
            url = f"http://127.0.0.1:5000/api/predict?model_key={m}&split={s}&max_points=500"
            try:
                req = urllib.request.urlopen(url)
                p_data = json.loads(req.read().decode('utf-8'))
                with open(out_file, 'w', encoding='utf-8') as f:
                    json.dump(p_data, f)
                print(f"    [+] Cached data/predict_{m}_{s}.json ({len(p_data.get('timestamps', []))} pts)")
            except Exception as e:
                print(f"    [-] Error caching {m}_{s}: {e}")

    # 6. Generate _redirects for Netlify
    redirects_content = """# Netlify Clean URLs and Routing Rules
/api/chat       /.netlify/functions/chat 200
/plot           /plot.html              200
/v2             /index.html             200
/api/models     /data/models.json       200
/api/live_telemetry /data/telemetry.json 200
/api/forecast   /.netlify/functions/forecast  200
/api/readings   /.netlify/functions/readings  200
/api/auth/generate-key /.netlify/functions/generate-key  200
/api/register   /.netlify/functions/register  200
/api/login      /.netlify/functions/login  200
/api/me         /.netlify/functions/me  200
/api/logout     /.netlify/functions/logout  200
/history        /history.html           200

# Optional: If you deploy your Flask backend to Render/Railway, proxy all /api calls:
# /api/*  https://YOUR-FLASK-APP.onrender.com/api/:splat  200
"""
    with open(os.path.join(DIST_DIR, '_redirects'), 'w', encoding='utf-8') as f:
        f.write(redirects_content)
    print("  [+] Generated dist/_redirects")

    # 7. Generate netlify.toml in project root
    netlify_toml_content = """[build]
  publish = "dist"
  functions = "netlify/functions"

[[redirects]]
  from = "/api/chat"
  to = "/.netlify/functions/chat"
  status = 200

[[redirects]]
  from = "/plot"
  to = "/plot.html"
  status = 200

[[redirects]]
  from = "/v2"
  to = "/index.html"
  status = 200

[[redirects]]
  from = "/api/models"
  to = "/data/models.json"
  status = 200

[[redirects]]
  from = "/api/live_telemetry"
  to = "/data/telemetry.json"
  status = 200

[[redirects]]
  from = "/api/forecast"
  to = "/.netlify/functions/forecast"
  status = 200

[[redirects]]
  from = "/api/readings"
  to = "/.netlify/functions/readings"
  status = 200

[[redirects]]
  from = "/api/auth/generate-key"
  to = "/.netlify/functions/generate-key"
  status = 200

[[redirects]]
  from = "/api/register"
  to = "/.netlify/functions/register"
  status = 200

[[redirects]]
  from = "/api/login"
  to = "/.netlify/functions/login"
  status = 200

[[redirects]]
  from = "/api/me"
  to = "/.netlify/functions/me"
  status = 200

[[redirects]]
  from = "/api/logout"
  to = "/.netlify/functions/logout"
  status = 200

[[redirects]]
  from = "/history"
  to = "/history.html"
  status = 200

# Optional: If you connect a live Python backend on Render, Railway, or Fly.io:
# [[redirects]]
#   from = "/api/*"
#   to = "https://YOUR-FLASK-BACKEND.onrender.com/api/:splat"
#   status = 200
"""
    with open(os.path.join(BASE_DIR, 'netlify.toml'), 'w', encoding='utf-8') as f:
        f.write(netlify_toml_content)
    print("  [+] Generated netlify.toml in project root")

    print("\n[SUCCESS] Netlify static distribution built successfully in 'dist/'.")

if __name__ == '__main__':
    build()
