from fastapi import APIRouter
from services.tts_service import text_to_speech

router = APIRouter()
router.add_api_route("/tts", text_to_speech, methods=["GET"])
