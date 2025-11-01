import json
from core.config import sessions, session_id

async def broadcast(message: dict):
    if session_id not in sessions:
        return
    for ws in list(sessions[session_id]["clients"].keys()):
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            pass
