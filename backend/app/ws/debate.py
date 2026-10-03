"""WebSocket debate channel."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.engine import handle_user_turn

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/debate")
async def debate_ws(ws: WebSocket):
	await ws.accept()
	try:
		while True:
			raw = await ws.receive_text()
			try:
				msg = json.loads(raw)
			except json.JSONDecodeError:
				await ws.send_json({"type": "error", "message": "JSON invalide"})
				continue

			mtype = msg.get("type") or "user_message"
			if mtype == "ping":
				await ws.send_json({"type": "pong"})
				continue

			player_role = str(msg.get("role") or "accuse")
			user_text = str(msg.get("text") or "").strip()
			if not user_text:
				await ws.send_json({"type": "error", "message": "texte vide"})
				continue

			case: dict[str, Any] = msg.get("case") or {}
			history = msg.get("history") or []
			if not isinstance(history, list):
				history = []
			mode = str(msg.get("mode") or "chaos")
			npc_cursor = int(msg.get("npcCursor") or 0)
			voice = msg.get("voice") if isinstance(msg.get("voice"), dict) else None

			async for event in handle_user_turn(
				player_role=player_role,
				user_text=user_text,
				case=case,
				history=[{"speaker": str(h.get("speaker", "")), "text": str(h.get("text", ""))} for h in history],
				mode=mode,
				npc_cursor=npc_cursor,
				voice=voice,
			):
				await ws.send_json(event)
	except WebSocketDisconnect:
		logger.info("debate ws disconnected")
	except Exception as exc:
		logger.exception("debate ws error: %s", exc)
		try:
			await ws.send_json({"type": "error", "message": str(exc)})
		except Exception:
			pass
