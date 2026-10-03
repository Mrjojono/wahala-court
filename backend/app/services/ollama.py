"""Ollama client — streaming chat for Gemma."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def ping() -> bool:
	settings = get_settings()
	try:
		async with httpx.AsyncClient(timeout=3.0) as client:
			r = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
			return r.status_code == 200
	except Exception:
		return False


async def chat_stream(
	messages: list[dict[str, str]],
	*,
	model: str | None = None,
) -> AsyncIterator[str]:
	"""Yield text tokens from Ollama /api/chat stream."""
	settings = get_settings()
	payload = {
		"model": model or settings.ollama_model,
		"messages": messages,
		"stream": True,
		"options": {"temperature": 0.85, "num_predict": 220},
	}
	url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
	try:
		async with httpx.AsyncClient(timeout=120.0) as client:
			async with client.stream("POST", url, json=payload) as resp:
				if resp.status_code >= 400:
					body = await resp.aread()
					logger.warning("Ollama chat error %s: %s", resp.status_code, body[:300])
					return
				async for line in resp.aiter_lines():
					if not line:
						continue
					try:
						chunk = json.loads(line)
					except json.JSONDecodeError:
						continue
					msg = chunk.get("message") or {}
					token = msg.get("content") or ""
					if token:
						yield token
					if chunk.get("done"):
						break
	except Exception as exc:
		logger.warning("Ollama stream failed: %s", exc)
		return


async def chat_complete(messages: list[dict[str, str]], *, model: str | None = None) -> str:
	parts: list[str] = []
	async for token in chat_stream(messages, model=model):
		parts.append(token)
	return "".join(parts).strip()
