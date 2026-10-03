"""JSON helpers for small local models (Gemma)."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_json_object(raw: str) -> dict[str, Any] | None:
	text = (raw or "").strip()
	if not text:
		return None
	if text.startswith("```"):
		text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
		text = re.sub(r"\s*```$", "", text)
	try:
		data = json.loads(text)
		return data if isinstance(data, dict) else None
	except json.JSONDecodeError:
		pass
	m = re.search(r"\{[\s\S]*\}", text)
	if not m:
		return None
	try:
		data = json.loads(m.group(0))
		return data if isinstance(data, dict) else None
	except json.JSONDecodeError:
		return None
