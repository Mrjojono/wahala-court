"""Unified LLM: Ollama (local) → Google AI Studio Gemma (cloud key)."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def ollama_up() -> bool:
	settings = get_settings()
	try:
		async with httpx.AsyncClient(timeout=2.5) as client:
			r = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
			return r.status_code == 200
	except Exception:
		return False


def cloud_configured() -> bool:
	s = get_settings()
	return bool(s.gemini_api_key.strip())


async def ping() -> dict[str, Any]:
	local = await ollama_up()
	cloud = cloud_configured()
	return {
		"ollama": local,
		"cloud": cloud,
		"ready": local or cloud,
		"provider": "ollama" if local else ("cloud" if cloud else "none"),
	}


def _to_gemini_contents(messages: list[dict[str, str]]) -> tuple[str | None, list[dict[str, Any]]]:
	system_parts: list[str] = []
	contents: list[dict[str, Any]] = []
	for m in messages:
		role = m.get("role") or "user"
		text = m.get("content") or ""
		if role == "system":
			system_parts.append(text)
			continue
		grole = "model" if role == "assistant" else "user"
		contents.append({"role": grole, "parts": [{"text": text}]})
	sys = "\n\n".join(system_parts) if system_parts else None
	if not contents:
		contents = [{"role": "user", "parts": [{"text": "Réponds."}]}]
	return sys, contents


async def _cloud_complete(messages: list[dict[str, str]], *, model: str | None = None) -> str:
	settings = get_settings()
	key = settings.gemini_api_key.strip()
	if not key:
		return ""
	model_id = model or settings.gemma_cloud_model
	sys, contents = _to_gemini_contents(messages)
	url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
	body: dict[str, Any] = {
		"contents": contents,
		"generationConfig": {"temperature": 0.85, "maxOutputTokens": 512},
	}
	if sys:
		body["systemInstruction"] = {"parts": [{"text": sys}]}
	try:
		async with httpx.AsyncClient(timeout=90.0) as client:
			r = await client.post(url, params={"key": key}, json=body)
			if r.status_code >= 400:
				logger.warning("Gemma cloud error %s: %s", r.status_code, r.text[:400])
				return ""
			data = r.json()
			cands = data.get("candidates") or []
			if not cands:
				return ""
			parts = (((cands[0] or {}).get("content") or {}).get("parts")) or []
			texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
			return "".join(texts).strip()
	except Exception as exc:
		logger.warning("Gemma cloud failed: %s", exc)
		return ""


async def _ollama_stream(
	messages: list[dict[str, str]], *, model: str | None = None
) -> AsyncIterator[str]:
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


async def chat_stream(
	messages: list[dict[str, str]], *, model: str | None = None
) -> AsyncIterator[str]:
	"""Prefer local Ollama; else cloud Gemma (fake-stream by chunks)."""
	if await ollama_up():
		async for t in _ollama_stream(messages, model=model):
			yield t
		return

	full = await _cloud_complete(messages, model=model)
	if not full:
		return
	buf = ""
	for ch in full:
		buf += ch
		if ch in " \n.,;:!?" or len(buf) >= 10:
			yield buf
			buf = ""
	if buf:
		yield buf


async def chat_complete(messages: list[dict[str, str]], *, model: str | None = None) -> str:
	if await ollama_up():
		parts: list[str] = []
		async for t in _ollama_stream(messages, model=model):
			parts.append(t)
		return "".join(parts).strip()
	return await _cloud_complete(messages, model=model)
