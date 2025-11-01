from fastapi import APIRouter
from starlette.responses import FileResponse, Response

router = APIRouter()

@router.get("/")
def home():
    return FileResponse("static/index.html")

@router.get("/static/recorder-worklet.js")
def get_worklet():
    return Response(open("static/recorder-worklet.js").read(), media_type="application/javascript")
