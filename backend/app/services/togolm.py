"""TogoLM client — retrieval only (search + document snippets)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def ping() -> bool:
	settings = get_settings()
	try:
		async with httpx.AsyncClient(timeout=8.0) as client:
			r = await client.get(f"{settings.togolm_base_url.rstrip('/')}/stats")
			return r.status_code == 200
	except Exception:
		return False


async def search(query: str, *, top_k: int = 4, category: str | None = "legal") -> list[dict[str, Any]]:
	"""Full-text search over the Togolese corpus. Returns normalized snippets."""
	settings = get_settings()
	q = (query or "").strip()
	if len(q) < 3:
		return []

	params: dict[str, Any] = {"q": q[:400]}
	# API accepts optional filters; category may be ignored by some builds
	if category:
		params["category"] = category

	headers: dict[str, str] = {}
	if settings.togolm_api_key:
		headers["X-API-Key"] = settings.togolm_api_key

	url = f"{settings.togolm_base_url.rstrip('/')}/search"
	try:
		async with httpx.AsyncClient(timeout=20.0) as client:
			r = await client.get(url, params=params, headers=headers)
			r.raise_for_status()
			payload = r.json()
	except Exception as exc:
		logger.warning("TogoLM search failed: %s", exc)
		return []

	raw = payload.get("results") or payload.get("documents") or payload.get("items") or []
	if isinstance(payload, list):
		raw = payload

	out: list[dict[str, Any]] = []
	for item in raw[:top_k]:
		if not isinstance(item, dict):
			continue
		out.append(
			{
				"id": str(item.get("id") or ""),
				"title": str(item.get("title") or "Document"),
				"url": item.get("url"),
				"excerpt": str(item.get("excerpt") or item.get("snippet") or item.get("text") or "")[:600],
				"source": str(item.get("source") or ""),
				"score": float(item.get("score") or 0),
				"category": item.get("category"),
			}
		)
	return out
