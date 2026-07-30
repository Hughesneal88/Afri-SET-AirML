from flask import Blueprint, request, jsonify, session
from web_app.db import create_user, authenticate_user, get_user_by_id

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def api_register():
    try:
        payload = request.get_json() or {}
        username = payload.get('username', '').strip()
        email = payload.get('email', '').strip()
        password = payload.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        if len(password) < 6:
            return jsonify({"status": "error", "message": "Password must be at least 6 characters."}), 400

        user = create_user(username, email, password)
        if not user:
            return jsonify({"status": "error", "message": "Username or email already exists."}), 400

        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            "status": "success",
            "message": "Account created successfully!",
            "user": user
        })
    except Exception as e:
        print(f"Auth register error: {e}")
        return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 500

@auth_bp.route('/login', methods=['POST'])
def api_login():
    try:
        payload = request.get_json() or {}
        username_or_email = payload.get('username', '').strip()
        password = payload.get('password', '').strip()

        if not username_or_email or not password:
            return jsonify({"status": "error", "message": "Please enter username/email and password."}), 400

        user = authenticate_user(username_or_email, password)
        if not user:
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401

        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            "status": "success",
            "message": "Welcome back!",
            "user": user
        })
    except Exception as e:
        print(f"Auth login error: {e}")
        return jsonify({"status": "error", "message": "Login failed. Please try again."}), 500

@auth_bp.route('/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out."})

@auth_bp.route('/me', methods=['GET'])
def api_me():
    try:
        user_id = session.get('user_id')
        if user_id:
            user = get_user_by_id(user_id)
            if user:
                return jsonify({"status": "success", "user": user})
    except Exception as e:
        print(f"Auth me check error: {e}")

    return jsonify({"status": "guest", "user": None})
