import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from web_app.app_factory import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Modular AirML Studio Server (Zero SPOF Architecture) on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, threaded=True, debug=False)
