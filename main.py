from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes.static_route import router as static_router
from routes.tts_route import router as tts_router
from routes.websocket_route import router as ws_router
from database.session import init_db

app = FastAPI(title="Doctor-Patient Transcription App")


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(static_router)
app.include_router(tts_router)
app.include_router(ws_router)

init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
