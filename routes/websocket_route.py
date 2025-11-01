import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.config import sessions, session_id, TRANSCRIBE_INTERVAL
from services.whisper_service import save_and_transcribe
from core.summarizer import summarize_conversation

router = APIRouter()

@router.websocket("/ws/whisper")
async def websocket_endpoint(ws: WebSocket, role: str = Query(...)):
    await ws.accept()
    if session_id not in sessions:
        sessions[session_id] = {"clients": {}, "transcript": []}
    sessions[session_id]["clients"][ws] = {"role": role, "sample_rate": None}
    print(f"{role} connected ✅")

    audio_buffer = []
    async def periodic_transcriber():
        nonlocal audio_buffer
        while True:
            await asyncio.sleep(TRANSCRIBE_INTERVAL)
            if audio_buffer:
                frames = audio_buffer.copy()
                audio_buffer = []
                await save_and_transcribe(frames, role, ws)

    task = asyncio.create_task(periodic_transcriber())
    try:
        while True:
            msg = await ws.receive()
            if msg.get("bytes"):
                audio_buffer.append(msg["bytes"])
            elif msg.get("text"):
                js = json.loads(msg["text"])
                if js.get("type") == "meta":
                    sr = int(js.get("sampleRate", 16000))
                    sessions[session_id]["clients"][ws]["sample_rate"] = sr
    except WebSocketDisconnect:
        print(f"{role} disconnected ❌")
    finally:
        task.cancel()
        if audio_buffer:
            await save_and_transcribe(audio_buffer.copy(), role, ws)
        if not sessions[session_id]["clients"]:
            summary = summarize_conversation("\n".join(sessions[session_id]["transcript"]))
            print("🧾 Summary:", summary)
