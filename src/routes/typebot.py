from flask import Blueprint
import requests
import os

typebot_bp = Blueprint('typebot', __name__)


def send_to_typebot(session_id, message):
    """Envia mensagem para o Typebot"""
    try:
        typebot_url = os.environ.get('TYPEBOT_VIEWER_URL', 'http://localhost:3001')
        typebot_id = os.environ.get('TYPEBOT_ID', 'default')

        payload = {
            "message": message,
            "sessionId": session_id,
        }

        response = requests.post(
            f"{typebot_url}/api/v1/{typebot_id}/message",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout as e:
        print(f"Timeout error while contacting Typebot: {e}")
        return {"error": "Typebot request timed out"}
    except Exception as e:
        return {"error": str(e)}
