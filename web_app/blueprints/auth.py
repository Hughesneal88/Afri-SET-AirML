from flask import Blueprint, request, jsonify, session
from web_app.db import (
    create_user_with_unique_key,
    authenticate_user_by_unique_key,
    create_user,
    authenticate_user,
    get_user_by_id,
    generate_unique_string_key
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/auth/generate-key', methods=['POST'])
def api_generate_key():
    """Generates a new unique access string key and creates an account."""
    try:
        payload = request.get_json() or {}
        username = payload.get('username', '').strip()
        custom_key = payload.get('unique_key', '').strip()
        
        user = create_user_with_unique_key(username=username, custom_key=custom_key)
        if not user:
            return jsonify({"status": "error", "message": "Could not generate unique key. Please try again."}), 400

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['unique_key'] = user['unique_key']

        return jsonify({
            "status": "success",
            "message": "Unique Access Key generated successfully!",
            "user": user,
            "unique_key": user['unique_key']
        })
    except Exception as e:
        print(f"Auth generate-key error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@auth_bp.route('/register', methods=['POST'])
def api_register():
    """
    Registers a user using their Unique Access String (passwordless).
    If a password is also sent (legacy), it gracefully handles it.
    """
    try:
        payload = request.get_json() or {}
        unique_key = (payload.get('unique_key') or payload.get('key') or '').strip()
        username = payload.get('username', '').strip()
        password = payload.get('password', '').strip()

        # If user did not provide a unique_key, generate one automatically
        if not unique_key and not password:
            unique_key = generate_unique_string_key()

        if unique_key:
            user = create_user_with_unique_key(username=username, custom_key=unique_key)
            if not user:
                return jsonify({"status": "error", "message": "Unique key already exists or is invalid. Please pick another or generate one."}), 400
        else:
            # Legacy password fallback if requested
            email = payload.get('email', f"{username.lower()}@airsense.local")
            user = create_user(username, email, password)
            if not user:
                return jsonify({"status": "error", "message": "User already exists."}), 400

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['unique_key'] = user.get('unique_key', unique_key)

        return jsonify({
            "status": "success",
            "message": "Account created successfully with Unique Access String!",
            "user": user,
            "unique_key": user.get('unique_key', unique_key)
        })
    except Exception as e:
        print(f"Auth register error: {e}")
        return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 500


@auth_bp.route('/login', methods=['POST'])
def api_login():
    """
    Authenticates a user via their Unique Access String.
    Also supports legacy username/password if provided.
    """
    try:
        payload = request.get_json() or {}
        unique_key = (payload.get('unique_key') or payload.get('key') or payload.get('username') or '').strip()
        password = payload.get('password', '').strip()

        user = None
        # 1. First attempt Unique Key authentication
        if unique_key:
            user = authenticate_user_by_unique_key(unique_key)

        # 2. If password provided and unique_key lookup didn't match, attempt legacy authentication
        if not user and password and unique_key:
            user = authenticate_user(unique_key, password)

        if not user:
            return jsonify({
                "status": "error",
                "message": "Invalid Unique Access Key. Please check the string and try again, or generate a new key."
            }), 401

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['unique_key'] = user.get('unique_key')

        return jsonify({
            "status": "success",
            "message": f"Welcome back, {user['username']}!",
            "user": user,
            "unique_key": user.get('unique_key')
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
                return jsonify({
                    "status": "success",
                    "authenticated": True,
                    "user": user,
                    "unique_key": user.get('unique_key')
                })
    except Exception as e:
        print(f"Auth me check error: {e}")

    return jsonify({"status": "guest", "authenticated": False, "user": None})
