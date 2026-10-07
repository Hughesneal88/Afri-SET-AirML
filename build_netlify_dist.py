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
