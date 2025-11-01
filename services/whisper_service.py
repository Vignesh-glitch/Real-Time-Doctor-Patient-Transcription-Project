import tempfile, os, numpy as np, soundfile as sf, asyncio, json
from sqlmodel import Session
from faster_whisper import WhisperModel
from database.models import Transcript
from database.session import engine
from core.helpers import is_speech, resample_audio_if_needed, trim_silence
from core.config import SAMPLE_RATE, sessions, session_id
from services.diarization_service import diarization_pipeline
from services.translation_service import translator
from core.broadcast import broadcast

model = WhisperModel("medium", device="cpu", compute_type="int8")
print("✅ Whisper model loaded")

async def save_and_transcribe(audio_frames, role, ws):
    print(f"🔊 Received {len(audio_frames)} frames from {role}")
    if not audio_frames:
        return
    audio_data = b"".join(audio_frames)
    audio_int16 = np.frombuffer(audio_data, dtype=np.int16)
    audio_float = audio_int16.astype(np.float32) / 32768.0

    client_meta = sessions.get(session_id, {}).get("clients", {}).get(ws, {})
    client_sr = client_meta.get("sample_rate", SAMPLE_RATE)
    audio_float = resample_audio_if_needed(audio_float, client_sr, SAMPLE_RATE)
    audio_float = trim_silence(audio_float)

    if not is_speech(audio_float):
        print("Skipped low-energy chunk.")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio_float, SAMPLE_RATE)
        tmp_path = tmp.name

    segments, _ = model.transcribe(tmp_path, beam_size=5, language="en")
    text = " ".join([s.text for s in segments if s.text]).strip()

    if text:
        with Session(engine) as db:
            db.add(Transcript(role=role, text=text))
            db.commit()

    payload = {"type": "stt", "role": role, "is_final": True, "text": text}
    await broadcast(payload)
    sessions[session_id]["transcript"].append(f"{role}: {text}")

    os.remove(tmp_path)
