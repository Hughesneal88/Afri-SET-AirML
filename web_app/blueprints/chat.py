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
    update_session_title, delete_session
)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')
rag_engine = AirQualityRAGEngine(BASE_DIR)
quantaq_client = QuantAQClient(BASE_DIR)

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    try:
        user_id = session.get('user_id')
        sessions = list_user_sessions(user_id=user_id)
        return jsonify({"status": "success", "sessions": sessions})
    except Exception as e:
        print(f"Get chat sessions error: {e}")
        return jsonify({"status": "error", "sessions": []}), 500

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    try:
        messages = get_session_messages(session_id)
        return jsonify({"status": "success", "session_id": session_id, "messages": messages})
    except Exception as e:
        print(f"Get chat history error ({session_id}): {e}")
        return jsonify({"status": "error", "messages": []}), 500

@chat_bp.route('/chat/new', methods=['POST'])
def new_chat_session():
    try:
        user_id = session.get('user_id')
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

@chat_bp.route('/chat', methods=['POST'])
def api_chat_message():
    try:
        payload = request.get_json() or {}
        query = payload.get('query', '').strip()
        session_id = payload.get('session_id')
        model_key = payload.get('model_key', 'random_forest_pm25_model_update2')

        if not query:
            return jsonify({"status": "error", "message": "Query cannot be empty."}), 400

        user_id = session.get('user_id')
        
        chat_sess = get_or_create_session(session_id=session_id, user_id=user_id, title=query[:50])
        session_id = chat_sess["session_id"]

        existing_messages = get_session_messages(session_id)
        if len(existing_messages) == 0:
            update_session_title(session_id, query[:50])

        add_chat_message(session_id=session_id, role="user", content=query)

        live_telemetry = quantaq_client.calibrate_live_telemetry()

        registry = discover_joblib_models()
        active_model_name = registry.get(model_key, {}).get('name', 'Random Forest Regressor')

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

        add_chat_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            llm_engine=llm_engine,
            citations_json=citations_json
        )

        updated_messages = get_session_messages(session_id)

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_engine": llm_engine,
            "retrieved_context": citations,
            "messages": updated_messages
        })
    except Exception as e:
        print(f"Chat API exception: {e}")
        return jsonify({"status": "error", "message": f"AirSense AI error: {str(e)}"}), 500

@chat_bp.route('/rag_query', methods=['POST'])
def rag_query():
    return api_chat_message()
