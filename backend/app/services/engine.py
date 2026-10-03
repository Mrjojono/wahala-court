"""Debate engine: TogoLM retrieve → Gemma generate (+ mock fallback)."""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from typing import Any

from app.services import mock as mock_svc
from app.services import llm as ollama_svc
from app.services import togolm as togolm_svc
from app.services.jsonutil import parse_json_object
from app.services.prompts import (
	chamber_messages,
	debate_messages,
	depot_messages,
	extract_law_cite,
	letter_messages,
	pick_npc_cast,
	pick_npc_speaker,
	post_messages,
	voice_messages,
)

logger = logging.getLogger(__name__)


async def _llm_ready() -> bool:
	st = await ollama_svc.ping()
	return bool(st.get("ready"))



def _search_query(case: dict[str, Any], history: list[dict[str, str]]) -> str:
	bits = [
		str(case.get("charge") or ""),
		str(case.get("context") or ""),
		str(case.get("category") or ""),
	]
	if history:
		bits.append(str(history[-1].get("text") or "")[:160])
	bits.append("droit obligation responsabilité contrat")
	return " ".join(b for b in bits if b).strip()


async def retrieve_context(case: dict[str, Any], history: list[dict[str, str]]) -> list[dict[str, Any]]:
	q = _search_query(case, history)
	return await togolm_svc.search(q, top_k=4, category="legal")


async def _stream_text_as_tokens(speaker: str, text: str) -> AsyncIterator[dict[str, Any]]:
	buf = ""
	for ch in text:
		buf += ch
		if ch in " \n.,;:!?" or len(buf) >= 8:
			yield {"type": "token", "speaker": speaker, "text": buf}
			buf = ""
	if buf:
		yield {"type": "token", "speaker": speaker, "text": buf}


async def stream_reply(
	*,
	speaker: str,
	case: dict[str, Any],
	history: list[dict[str, str]],
	mode: str = "chaos",
	snippets: list[dict[str, Any]] | None = None,
	voice: dict[str, Any] | None = None,
	emit_sources: bool = True,
) -> AsyncIterator[dict[str, Any]]:
	snips = snippets if snippets is not None else await retrieve_context(case, history)
	if emit_sources:
		yield {"type": "sources", "sources": snips}
	yield {"type": "typing", "speaker": speaker}

	if not await _llm_ready():
		fallback = next((m for m in mock_svc.MOCK_LINES if m["speaker"] == speaker), mock_svc.MOCK_LINES[0])
		text = fallback["text"]
		async for ev in _stream_text_as_tokens(speaker, text):
			yield ev
		yield {
			"type": "line",
			"id": f"mock-{int(time.time() * 1000)}-{speaker}",
			"speaker": speaker,
			"text": text,
			"lawCite": fallback.get("lawCite") or None,
			"fallback": True,
		}
		return

	messages = debate_messages(
		speaker=speaker,
		case=case,
		history=history,
		mode=mode,
		snippets=snips,
		voice=voice,
	)
	buf: list[str] = []
	async for token in ollama_svc.chat_stream(messages):
		buf.append(token)
		yield {"type": "token", "speaker": speaker, "text": token}

	full = "".join(buf).strip()
	if not full:
		full = "La Cour… a besoin d'un café. (réplique vide — réessayez)"
		yield {"type": "token", "speaker": speaker, "text": full}

	yield {
		"type": "line",
		"id": f"ai-{int(time.time() * 1000)}-{speaker}",
		"speaker": speaker,
		"text": full,
		"lawCite": extract_law_cite(full),
		"fallback": False,
	}


async def handle_user_turn(
	*,
	player_role: str,
	user_text: str,
	case: dict[str, Any],
	history: list[dict[str, str]],
	mode: str = "chaos",
	npc_cursor: int = 0,
	voice: dict[str, Any] | None = None,
) -> AsyncIterator[dict[str, Any]]:
	"""Player speaks once → Gemma plays the other cast roles in sequence."""
	hist = list(history)
	hist.append({"speaker": player_role, "text": user_text})
	cast = pick_npc_cast(player_role, count=3)
	snips = await retrieve_context(case, hist)
	cursor = npc_cursor

	if not await _llm_ready():
		yield {"type": "sources", "sources": snips}
		for i, _speaker in enumerate(cast):
			line, cursor = mock_svc.next_mock(player_role, cursor)
			if not line:
				break
			yield {"type": "typing", "speaker": line["speaker"]}
			async for ev in _stream_text_as_tokens(line["speaker"], line["text"]):
				yield ev
			yield {
				"type": "line",
				"id": f"mock-{int(time.time() * 1000)}-{i}",
				"speaker": line["speaker"],
				"text": line["text"],
				"lawCite": line.get("lawCite") or None,
				"fallback": True,
				"npcCursor": cursor,
			}
			hist.append({"speaker": line["speaker"], "text": line["text"]})
		yield {"type": "done", "npcCursor": cursor}
		return

	for i, npc in enumerate(cast):
		async for ev in stream_reply(
			speaker=npc,
			case=case,
			history=hist,
			mode=mode,
			snippets=snips,
			voice=voice,
			emit_sources=(i == 0),
		):
			yield ev
			if ev.get("type") == "line":
				hist.append({"speaker": str(ev.get("speaker")), "text": str(ev.get("text"))})
	yield {"type": "done", "npcCursor": cursor}


def _chamber_fallback(people_vote: str, case: dict[str, Any]) -> dict[str, Any]:
	# Slightly invert people ~40% of the time via hash of case number for demo drama
	num = str(case.get("number") or "")
	invert = sum(ord(c) for c in num) % 5 == 0
	outcome = people_vote
	if invert:
		outcome = "innocent" if people_vote == "coupable" else "coupable"
	headline = "COUPABLE" if outcome == "coupable" else "NON COUPABLE"
	sentence = (
		"Deux semaines de nettoyage du micro-ondes et interdiction d’approcher le frigo du 3ème."
		if outcome == "coupable"
		else "Acquittement avec avertissement solennel : le temps des autres n’est pas une ressource illimitée."
	)
	return {
		"procureur_closing": "Le prévenu a transformé l'espoir collectif en mensonge chronométré.",
		"defense_closing": "Votre Honneur, « j'arrive » est une intention, pas un contrat OHADA.",
		"outcome": outcome,
		"headline": headline,
		"sentence": sentence,
		"lawCite": "Art. 419-B · Crimes de pause & promesses",
		"dissent": "La chambre note un wahala plus culturel que criminel.",
		"wahalaScore": 72 if outcome == "coupable" else 38,
		"rationale": (
			"Le tribunal contredit le peuple pour rappeler la nuance."
			if outcome != people_vote
			else "Le tribunal confirme le peuple — les faits sont clairs."
		),
		"disagreesWithPeople": outcome != people_vote,
		"fallback": True,
		"sources": [],
	}


async def deliberate_chamber(
	*,
	case: dict[str, Any],
	transcript: list[dict[str, str]],
	people_vote: str,
	mode: str = "chaos",
	voice: dict[str, Any] | None = None,
) -> dict[str, Any]:
	vote = people_vote if people_vote in ("coupable", "innocent") else "coupable"
	snips = await retrieve_context(case, transcript)

	if not await _llm_ready():
		out = _chamber_fallback(vote, case)
		out["sources"] = snips
		return out

	raw = await ollama_svc.chat_complete(
		chamber_messages(
			case=case,
			transcript=transcript,
			people_vote=vote,
			mode=mode,
			snippets=snips,
			voice=voice,
		)
	)
	data = parse_json_object(raw) or {}
	outcome = str(data.get("outcome") or "").lower()
	if outcome not in ("coupable", "innocent"):
		fb = _chamber_fallback(vote, case)
		fb["sources"] = snips
		fb["raw"] = raw[:400]
		return fb

	headline = str(data.get("headline") or ("COUPABLE" if outcome == "coupable" else "NON COUPABLE"))
	return {
		"procureur_closing": str(data.get("procureur_closing") or ""),
		"defense_closing": str(data.get("defense_closing") or ""),
		"outcome": outcome,
		"headline": headline,
		"sentence": str(data.get("sentence") or _chamber_fallback(vote, case)["sentence"]),
		"lawCite": str(data.get("lawCite") or "Art. 1 · Délibération Gemma"),
		"dissent": str(data.get("dissent") or ""),
		"wahalaScore": int(data.get("wahalaScore") or 50),
		"rationale": str(data.get("rationale") or ""),
		"disagreesWithPeople": outcome != vote,
		"fallback": False,
		"sources": snips,
	}


async def extract_voice(*, raw: str, accused_name: str = "") -> dict[str, Any]:
	text = (raw or "").strip()
	fallback = {
		"tone": "nonchalant, défensif, blagueur",
		"lexicon": ["wallah", "frère", "j'arrive", "c'est chaud"],
		"excuses": ["j'étais en route", "mon réseau", "je t'appelle juste après"],
		"catchphrases": ["5 minutes"],
		"summary": "Pote qui promet vite et arrive tard.",
		"fallback": True,
	}
	if len(text) < 8:
		return fallback
	if not await _llm_ready():
		# Heuristic lite from pasted text
		words = [w.strip(".,!?«»\"'") for w in text.lower().replace("\n", " ").split() if len(w) > 3]
		uniq = list(dict.fromkeys(words))[:6]
		if uniq:
			fallback["lexicon"] = uniq
		fallback["summary"] = f"Voix extraite (offline) pour {accused_name or 'le pote'}."
		return fallback

	raw_out = await ollama_svc.chat_complete(voice_messages(raw=text, accused_name=accused_name))
	data = parse_json_object(raw_out) or {}
	return {
		"tone": str(data.get("tone") or fallback["tone"]),
		"lexicon": list(data.get("lexicon") or fallback["lexicon"])[:8],
		"excuses": list(data.get("excuses") or fallback["excuses"])[:6],
		"catchphrases": list(data.get("catchphrases") or fallback["catchphrases"])[:4],
		"summary": str(data.get("summary") or fallback["summary"]),
		"fallback": False,
	}


async def generate_posts(entry: dict[str, Any], formats: list[str] | None = None) -> dict[str, Any]:
	fmts = formats or ["caption", "whatsapp", "dev"]
	case = entry.get("caseFile") or entry.get("case") or {}
	verdict = entry.get("verdict") or {}

	fallback = {
		"caption": (
			f"WAHALA COURT · {case.get('number', '')} · {verdict.get('headline', 'VERDICT')} — "
			f"{verdict.get('sentence', '')}"
		)[:280],
		"whatsapp": (
			f"Tribunal de Wahala 🏛️\n"
			f"{case.get('charge', '')}\n"
			f"Verdict: {verdict.get('headline', '')}\n"
			f"{verdict.get('sentence', '')}\n"
			f"#{case.get('number', 'WC')}"
		),
		"dev": (
			f"# Wahala Court — {case.get('number', '')}\n\n"
			f"**Charge:** {case.get('charge', '')}\n\n"
			f"**Verdict:** {verdict.get('headline', '')}\n\n"
			f"{verdict.get('sentence', '')}\n\n"
			f"_Généré en fallback (Ollama offline)._"
		),
		"fallback": True,
	}

	if not await _llm_ready():
		return fallback

	raw = await ollama_svc.chat_complete(post_messages(entry=entry, formats=fmts))
	data = parse_json_object(raw)
	if not data:
		fallback["dev"] = raw or fallback["dev"]
		return fallback
	return {
		"caption": str(data.get("caption") or fallback["caption"]),
		"whatsapp": str(data.get("whatsapp") or fallback["whatsapp"]),
		"dev": str(data.get("dev") or fallback["dev"]),
		"fallback": False,
	}


async def build_depot(*, friend_name: str, raw: str) -> dict[str, Any]:
	name = (friend_name or "LE POTE").strip().upper() or "LE POTE"
	fallback_case = {
		"number": f"WC-{str(abs(hash(raw)) % 900 + 100)}",
		"accusedName": name,
		"charge": f"{name} est accusé·e d’un wahala digne d’audience.",
		"exhibit": f"« {(raw.strip().splitlines() or ['j’arrive'])[0][:120]} »",
		"context": "Affaire déposée par un ami pour le Tribunal de Wahala.",
		"category": "Amitié",
		"gravity": 6,
	}
	fallback_voice = {
		"tone": "nonchalant, défensif",
		"lexicon": ["frère", "wallah", "j’arrive"],
		"excuses": ["j’étais en route", "mon réseau"],
		"catchphrases": ["5 minutes"],
		"summary": f"Vibe de {name}.",
		"fallback": True,
	}
	if not await _llm_ready():
		return {"caseFile": fallback_case, "voice": fallback_voice, "friendName": name, "fallback": True}

	raw_out = await ollama_svc.chat_complete(depot_messages(friend_name=name, raw=raw))
	data = parse_json_object(raw_out) or {}
	cats = {"Dating", "Amitié", "Famille", "WhatsApp", "Transport", "Argent", "Travail"}
	cat = str(data.get("category") or "Amitié")
	if cat not in cats:
		cat = "Amitié"
	voice = data.get("voice") if isinstance(data.get("voice"), dict) else {}
	case_file = {
		"number": f"WC-{str(abs(hash(raw + name)) % 900 + 100)}",
		"accusedName": str(data.get("accusedName") or name).upper(),
		"charge": str(data.get("charge") or fallback_case["charge"]),
		"exhibit": str(data.get("exhibit") or fallback_case["exhibit"]),
		"context": str(data.get("context") or fallback_case["context"]),
		"category": cat,
		"gravity": int(data.get("gravity") or 6),
	}
	voice_out = {
		"tone": str(voice.get("tone") or fallback_voice["tone"]),
		"lexicon": list(voice.get("lexicon") or fallback_voice["lexicon"])[:8],
		"excuses": list(voice.get("excuses") or fallback_voice["excuses"])[:6],
		"catchphrases": list(voice.get("catchphrases") or fallback_voice["catchphrases"])[:4],
		"summary": str(voice.get("summary") or fallback_voice["summary"]),
		"fallback": False,
	}
	return {"caseFile": case_file, "voice": voice_out, "friendName": name, "fallback": False}


async def write_friend_letter(
	*,
	friend_name: str,
	case: dict[str, Any],
	people_vote: str,
	verdict: dict[str, Any],
) -> dict[str, Any]:
	name = friend_name or case.get("accusedName") or "frère"
	fallback = {
		"opener": f"Yo {name}",
		"letter": (
			f"Yo {name},\n"
			f"On a jugé ton wahala au Tribunal. Le peuple : {people_vote}. "
			f"Le tribunal : {verdict.get('headline', '')}. "
			f"{verdict.get('sentence', '')}\n"
			f"Je t’envoie ça parce que t’es mon pote — et parce que Gemma a tourné en local/open. "
			f"Bisous, sans sursis."
		),
		"fallback": True,
	}
	if not await _llm_ready():
		return fallback
	raw = await ollama_svc.chat_complete(
		letter_messages(friend_name=name, case=case, people_vote=people_vote, verdict=verdict)
	)
	data = parse_json_object(raw) or {}
	letter = str(data.get("letter") or "").strip()
	if not letter:
		return fallback
	return {
		"opener": str(data.get("opener") or f"Yo {name}"),
		"letter": letter,
		"fallback": False,
	}
