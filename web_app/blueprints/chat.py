import json
import os
import sys
from flask import Blueprint, request, jsonify, session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from web_app.rag_engine import AirQualityRAGEngine
from web_app.quantaq_client import QuantAQClient
from web_app.blueprints.models import discover_joblib_models
from web_app.db import (
    get_or_create_session, list_user_sessions,
    add_chat_message, get_session_messages,
    update_session_title, delete_session,
    delete_all_user_sessions, authenticate_user_by_unique_key
)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')
rag_engine = AirQualityRAGEngine(BASE_DIR)
quantaq_client = QuantAQClient(BASE_DIR)

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Guest: sessions stored in browser only
            return jsonify({"status": "guest", "sessions": [], "message": "Guest sessions are stored locally in the browser."})
        sessions = list_user_sessions(user_id=user_id)
        return jsonify({"status": "success", "sessions": sessions})
    except Exception as e:
        print(f"Get chat sessions error: {e}")
        return jsonify({"status": "error", "sessions": []}), 500

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"status": "guest", "messages": [], "message": "Guest chats are stored locally in the browser."})
        messages = get_session_messages(session_id)
        return jsonify({"status": "success", "session_id": session_id, "messages": messages})
    except Exception as e:
        print(f"Get chat history error ({session_id}): {e}")
        return jsonify({"status": "error", "messages": []}), 500

@chat_bp.route('/chat/new', methods=['POST'])
def new_chat_session():
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Client manages guest session locally
            import uuid
            return jsonify({"status": "guest", "session": {"session_id": str(uuid.uuid4()), "title": "Guest Session"}})
        new_sess = get_or_create_session(user_id=user_id, title="New Conversation")
        return jsonify({"status": "success", "session": new_sess})
    except Exception as e:
        print(f"New chat session error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_bp.route('/chat/session/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    try:
        delete_session(session_id)
        return jsonify({"status": "success", "message": "Session deleted."})
    except Exception as e:
        print(f"Delete chat session error ({session_id}): {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_bp.route('/chat/history', methods=['DELETE'])
def delete_all_history():
    """Wipes all chat history for the currently logged in user."""
    try:
        user_id = session.get('user_id')
        if user_id:
            delete_all_user_sessions(user_id)
            return jsonify({"status": "success", "message": "All cloud chat sessions deleted successfully."})
        return jsonify({"status": "success", "message": "Guest chat cleared in browser."})
    except Exception as e:
        print(f"Delete all history error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_bp.route('/chat', methods=['POST'])
def api_chat_message():
    try:
        payload = request.get_json() or {}
        query = (payload.get('query') or payload.get('message') or '').strip()
        session_id = payload.get('session_id')
        model_key = payload.get('model_key', 'stacked_physics_meta_ensemble')
        browser_history = payload.get('history') or []

        if not query:
            return jsonify({"status": "error", "message": "Query cannot be empty."}), 400

        user_id = session.get('user_id')
        # Check header/payload for unique access key if session cookie was omitted
        if not user_id:
            key_in_req = payload.get('unique_key') or request.headers.get('X-Unique-Key')
            if key_in_req:
                u = authenticate_user_by_unique_key(key_in_req)
                if u:
                    user_id = u['id']
                    session['user_id'] = u['id']
                    session['username'] = u['username']

        is_logged_in = bool(user_id)
        existing_messages = []

        # 1. If logged in, manage conversation history in database
        if is_logged_in:
            chat_sess = get_or_create_session(session_id=session_id, user_id=user_id, title=query[:50])
            session_id = chat_sess["session_id"]
            existing_messages = get_session_messages(session_id)
            if len(existing_messages) == 0:
                update_session_title(session_id, query[:50])
            add_chat_message(session_id=session_id, role="user", content=query)
        else:
            # Guest: do NOT touch database. Use browser-supplied history for context
            existing_messages = browser_history
            if not session_id:
                session_id = "guest_browser_session"

        # 2. Retrieve live telemetry
        live_telemetry = quantaq_client.calibrate_live_telemetry()

        registry = discover_joblib_models()
        active_model_name = registry.get(model_key, {}).get('name', 'SPIME v4 Meta-Ensemble')

        # 3. Process RAG response
        rag_response = rag_engine.answer_user_question(
            query=query,
            live_telemetry=live_telemetry,
            active_model_name=active_model_name,
            chat_history=existing_messages
        )

        answer = rag_response.get("answer", "I could not generate an answer at this time.")
        llm_engine = rag_response.get("llm_engine", "AirSense AI Engine")
        citations = rag_response.get("retrieved_context", [])
        citations_json = json.dumps(citations) if citations else None
        plot_url = rag_response.get("plot_url")
        plot_title = rag_response.get("plot_title")

        # 4. If logged in, persist assistant answer to database
        if is_logged_in:
            add_chat_message(
                session_id=session_id,
                role="assistant",
                content=answer,
                llm_engine=llm_engine,
                citations_json=citations_json
            )
            updated_messages = get_session_messages(session_id)
        else:
            updated_messages = existing_messages + [
                {"role": "user", "content": query},
                {"role": "assistant", "content": answer, "llm_engine": llm_engine}
            ]

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_engine": llm_engine,
            "plot_url": plot_url,
            "plot_title": plot_title,
            "retrieved_context": citations,
            "messages": updated_messages,
            "persisted": is_logged_in,
            "storage_mode": "cloud_db" if is_logged_in else "browser_only"
        })
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        try:
            with open(os.path.join(PROJECT_DIR, "flask_errors.log"), "a", encoding="utf-8") as f:
                f.write(f"\n--- Chat API Exception ---\n{tb}\n")
        except Exception:
            pass
        return jsonify({"status": "error", "message": f"AirSense AI error: {str(e)}"}), 500

@chat_bp.route('/rag_query', methods=['POST'])
def rag_query():
    return api_chat_message()
