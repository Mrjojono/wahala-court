"""Wahala Court API — FastAPI entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.routes.chamber import router as chamber_router
from app.routes.posts import router as posts_router
from app.services import llm as ollama_svc
from app.services import togolm as togolm_svc
from app.ws.debate import router as debate_ws_router

settings = get_settings()

app = FastAPI(title="Wahala Court API", version="0.1.0")

_origins = settings.cors_origin_list
_allow_all = "*" in _origins
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"] if _allow_all else _origins,
	allow_credentials=not _allow_all,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(posts_router, prefix="/v1")
app.include_router(chamber_router, prefix="/v1")
app.include_router(debate_ws_router)


@app.get("/", response_class=PlainTextResponse)
@app.get("/ping", response_class=PlainTextResponse)
async def ping():
	return "pong"


@app.get("/health")
async def health():
	llm = await ollama_svc.ping()
	togolm_ok = await togolm_svc.ping()
	return {
		"ok": True,
		"ollama": llm["ollama"],
		"gemma_cloud": llm["cloud"],
		"llm_ready": llm["ready"],
		"provider": llm["provider"],
		"togolm": togolm_ok,
		"model": settings.ollama_model if llm["ollama"] else settings.gemma_cloud_model,
		"fallback": not llm["ready"],
	}
