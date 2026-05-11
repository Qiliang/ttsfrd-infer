import argparse
import json
import logging
import os
from contextlib import asynccontextmanager

import ttsfrd
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from rule import mail_replace
logger = logging.getLogger("ttsfrd-infer")
logging.basicConfig(level=logging.INFO)

RESOURCE_DIR = "/app/resource"
engine: ttsfrd.TtsFrontendEngine = None


def normalize_context_path(raw: str | None) -> str:
    if raw is None:
        raw = ""
    p = raw.strip().strip("/")
    return p if p else "ttsfrd"


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


class TextRequest(BaseModel):
    rules: list[str] = ["mail_replace"]
    text: str


class TextResponse(BaseModel):
    text: str


def normalize(text: str) -> str:
    result = json.loads(engine.do_voicegen_frd(text))
    return "".join(s["text"] for s in result["sentences"])


def build_app(context_path: str | None = None) -> FastAPI:
    """context_path: None 时使用环境变量 CONTEXT_PATH，默认为 ttsfrd。"""
    prefix = normalize_context_path(
        context_path if context_path is not None else os.environ.get("CONTEXT_PATH", "ttsfrd")
    )
    app = FastAPI(title="ttsfrd-infer", lifespan=lifespan)
    router = APIRouter()

    @router.get("/ping")
    def ping() -> TextResponse:
        return TextResponse(text="pong")

    @router.post("/api/transform")
    def ttsfrd_http(req: TextRequest) -> TextResponse:
        return TextResponse(text=normalize(req.text))

    @router.websocket("/api/transform")
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

    app.include_router(router, prefix=f"/{prefix}")
    logger.info("Serving under context path /%s", prefix)
    return app


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="ttsfrd-infer")
    parser.add_argument(
        "--context-path",
        default=None,
        help='HTTP 根路径（不含首尾斜杠），默认读取环境变量 CONTEXT_PATH 或 "ttsfrd"',
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(build_app(args.context_path), host=args.host, port=args.port)
else:
    app = build_app()
