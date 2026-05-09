import json
import logging
from contextlib import asynccontextmanager

import ttsfrd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from rule import mail_replace
logger = logging.getLogger("ttsfrd-infer")
logging.basicConfig(level=logging.INFO)

RESOURCE_DIR = "/app/resource"
engine: ttsfrd.TtsFrontendEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("Initializing ttsfrd engine...")
    engine = ttsfrd.TtsFrontendEngine()
    engine.initialize(RESOURCE_DIR)
    engine.set_lang_type("pinyinvg")
    logger.info("ttsfrd engine ready.")
    yield
    engine = None


app = FastAPI(title="ttsfrd-infer", lifespan=lifespan)


def normalize(text: str) -> str:
    result = json.loads(engine.do_voicegen_frd(text))
    return "".join(s["text"] for s in result["sentences"])


class TextRequest(BaseModel):
    rules: list[str] = ["mail_replace"]
    text: str


class TextResponse(BaseModel):
    text: str

@app.get("/ping")
def ping() -> TextResponse:
    return {TextResponse(text="pong")}

@app.post("/ttsfrd")
def ttsfrd_http(req: TextRequest) -> TextResponse:
    text = normalize(req.text)
    for rule in req.rules:
        text = globals()[rule](text)
    return TextResponse(text=text)


@app.websocket("/ttsfrd")
async def ttsfrd_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                text = payload.get("text", "")
            except (json.JSONDecodeError, AttributeError):
                text = data
            normalized = normalize(text)
            await websocket.send_text(json.dumps({"text": normalized}, ensure_ascii=False))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
