from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from gtts import gTTS
import tempfile, os

router = APIRouter()

@router.get("/tts")
async def text_to_speech(text: str, background_tasks: BackgroundTasks):
    tts = gTTS(text=text, lang="en")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    background_tasks.add_task(lambda: os.remove(tmp.name))
    return FileResponse(tmp.name, media_type="audio/mpeg")
