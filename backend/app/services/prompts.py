"""Prompt builders for debate, chamber, voice DNA, and posts."""

from __future__ import annotations

from typing import Any

PERSONA_HINTS = {
	"juge": "Tu es le juge du Tribunal de Wahala. Tu tranchés, tu rappelles l'ordre, ton est solennel mais piquant.",
	"procureur": "Tu es le procureur. Tu charges l'accusé, tu cites des 'articles', tu dramatises.",
	"defense": "Tu es l'avocat·e de la défense. Tu trouves des excuses culturelles, tu objectes, tu humanises.",
	"accuse": "Tu es l'accusé·e. Tu te justifies avec le ton réel d'un pote pris la main dans le sac.",
	"greffier": "Tu es le greffier. Tu annonces, tu résumes, zéro blabla.",
	"temoin": "Tu es un témoin. Tu reports ce que tu as 'vu' — version couloir.",
	"flat": "Tu es le public. Tu murmures, tu juges plus fort que le tribunal.",
}


def _format_sources(snippets: list[dict[str, Any]]) -> str:
	if not snippets:
		return "(aucun extrait corpus — invente un Art. comique plausible)"
	lines = []
	for i, s in enumerate(snippets, 1):
		title = s.get("title") or "Doc"
		excerpt = (s.get("excerpt") or "")[:280]
		src = s.get("source") or ""
		lines.append(f"{i}. [{src}] {title}\n   {excerpt}")
	return "\n".join(lines)


def _format_voice(voice: dict[str, Any] | None) -> str:
	if not voice:
		return ""
	lex = ", ".join(voice.get("lexicon") or [])
	exc = ", ".join(voice.get("excuses") or [])
	catch = ", ".join(voice.get("catchphrases") or [])
	tone = voice.get("tone") or ""
	return f"""
ADN du pote (imite ce style si tu parles pour l'accusé / la défense):
- Ton: {tone}
- Lexique: {lex or '—'}
- Excuses typiques: {exc or '—'}
- Catchphrases: {catch or '—'}
"""


def debate_messages(
	*,
	speaker: str,
	case: dict[str, Any],
	history: list[dict[str, str]],
	mode: str,
	snippets: list[dict[str, Any]],
	voice: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
	hint = PERSONA_HINTS.get(speaker, PERSONA_HINTS["procureur"])
	mode_line = (
		"Mode CHAOS: punchlines, exagération, humour togolais/couloir."
		if mode == "chaos"
		else "Mode SÉRIEUX: ton plus juridique, toujours un peu tabloïd."
	)
	system = f"""Tu joues dans Wahala Court, un procès comique des petits wahalas.
{hint}
{mode_line}
{_format_voice(voice)}
Règles:
- Réponds en français, 1 à 3 phrases max.
- Cite un « Art. X · titre » inspiré des extraits corpus (ou inventé si vide), style tabloïd.
- Ne révèle pas que tu es une IA.
- N'invente pas de violence réelle; reste light et partageable.

Dossier:
- N° {case.get('number', '?')}
- Charge: {case.get('charge', '')}
- Pièce: {case.get('exhibit', '')}
- Contexte: {case.get('context', '')}
- Catégorie: {case.get('category', '')}

Extraits TogoLM (corpus togolais — inspire-toi, adapté au wahala):
{_format_sources(snippets)}
"""
	msgs: list[dict[str, str]] = [{"role": "system", "content": system}]
	for h in history[-12:]:
		role = "assistant" if h.get("speaker") == speaker else "user"
		label = h.get("speaker", "?")
		msgs.append({"role": role, "content": f"[{label}] {h.get('text', '')}"})
	msgs.append(
		{
			"role": "user",
			"content": f"À toi de parler en tant que {speaker}. Une seule réplique d'audience.",
		}
	)
	return msgs


def chamber_messages(
	*,
	case: dict[str, Any],
	transcript: list[dict[str, str]],
	people_vote: str,
	mode: str,
	snippets: list[dict[str, Any]],
	voice: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
	lines = "\n".join(f"- [{t.get('speaker')}] {t.get('text')}" for t in transcript[-16:])
	mode_line = "Mode CHAOS" if mode == "chaos" else "Mode SÉRIEUX"
	system = f"""Tu es la CHAMBRE DU CONSEIL de Wahala Court — un mini tribunal multi-agents dans UN seul JSON.
Tu simules 3 cerveaux Gemma distincts qui se contredisent puis le juge tranche.
Le vote du PEUPLE est déjà connu: {people_vote}.
Tu peux ACCORDER ou CONTREDIRE le peuple — le contraste peuple vs tribunal est le cœur du produit.
{mode_line}. Français. Comique mais ancré dans les extraits.
{_format_voice(voice)}
Réponds UNIQUEMENT en JSON valide, sans markdown."""
	user = f"""Dossier {case.get('number')}:
Charge: {case.get('charge')}
Pièce: {case.get('exhibit')}
Contexte: {case.get('context')}
Catégorie: {case.get('category')}

Transcript:
{lines or '(vide)'}

Sources TogoLM:
{_format_sources(snippets)}

Schéma JSON strict:
{{
  "procureur_closing": "1-2 phrases",
  "defense_closing": "1-2 phrases",
  "outcome": "coupable" | "innocent",
  "headline": "COUPABLE" | "NON COUPABLE",
  "sentence": "peine comique 1 phrase",
  "lawCite": "Art. X · titre inspiré corpus",
  "dissent": "note de désaccord chambre (1 phrase)",
  "wahalaScore": 0-100,
  "rationale": "pourquoi le tribunal tranche ainsi vs le peuple (1 phrase)"
}}
"""
	return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def voice_messages(*, raw: str, accused_name: str) -> list[dict[str, str]]:
	system = """Tu extrais l'ADN stylistique d'un pote à partir de ses messages WhatsApp.
Réponds UNIQUEMENT en JSON valide, sans markdown."""
	user = f"""Nom: {accused_name or 'le pote'}
Messages:
{raw[:2500]}

Schéma:
{{
  "tone": "3-6 mots (ex: nonchalant, défensif, blagueur)",
  "lexicon": ["3 à 6 mots/expressions qu'il utilise"],
  "excuses": ["2 à 4 excuses typiques"],
  "catchphrases": ["1 à 3 catchphrases"],
  "summary": "une phrase qui capture sa vibe"
}}
"""
	return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def post_messages(*, entry: dict[str, Any], formats: list[str]) -> list[dict[str, str]]:
	case = entry.get("caseFile") or entry.get("case") or {}
	verdict = entry.get("verdict") or {}
	people = entry.get("peopleShare", 0)
	wanted = ", ".join(formats) if formats else "caption, whatsapp, dev"
	system = """Tu es rédacteur·ice du greffe de Wahala Court.
Produis des brouillons prêts à coller, en français, ton tabloïd africain francophone.
Réponds UNIQUEMENT en JSON valide avec les clés demandées, sans markdown."""
	user = f"""Affaire {case.get('number', '')}
Charge: {case.get('charge', '')}
Pièce: {case.get('exhibit', '')}
Verdict peuple/tribunal: {verdict.get('headline', verdict.get('outcome', ''))}
Sentence: {verdict.get('sentence', '')}
Article: {verdict.get('lawCite', '')}
Désaccord: {verdict.get('rationale', verdict.get('dissent', ''))}
Part peuple (approx): {people}%

Génère ces formats: {wanted}
Schéma JSON:
{{
  "caption": "texte court partage (max 280 car)",
  "whatsapp": "thread 3-5 lignes pour le groupe",
  "dev": "brouillon post DEV (titre + corps markdown court, mention open-source AI / Gemma / TogoLM ok)"
}}
"""
	return [
		{"role": "system", "content": system},
		{"role": "user", "content": user},
	]


def pick_npc_speaker(player_role: str) -> str:
	order = ["procureur", "defense", "accuse", "juge"]
	for s in order:
		if s != player_role:
			return s
	return "procureur"


def pick_npc_cast(player_role: str, *, count: int = 3) -> list[str]:
	"""Solo player → Gemma plays every other cast role (default all 3)."""
	if player_role == "juge":
		out = ["procureur", "defense", "accuse"]
	elif player_role == "procureur":
		out = ["defense", "accuse", "juge"]
	elif player_role == "defense":
		out = ["procureur", "accuse", "juge"]
	else:
		out = ["procureur", "defense", "juge"]
	return out[: max(1, min(count, len(out)))]


def extract_law_cite(text: str) -> str | None:
	import re

	m = re.search(r"(Art\.?\s*[\w.\-]+[^\n.]{0,60})", text, re.IGNORECASE)
	return m.group(1).strip() if m else None


def depot_messages(*, friend_name: str, raw: str) -> list[dict[str, str]]:
	system = """Tu es greffier comique de Wahala Court.
À partir d'un wahala raconté pour UN pote, tu montes un dossier de procès tabloïd.
Réponds UNIQUEMENT en JSON valide, sans markdown."""
	user = f"""Pote: {friend_name or 'le pote'}
Wahala / messages:
{raw[:3200]}

Schéma JSON:
{{
  "accusedName": "PRÉNOM EN MAJUSCULES",
  "charge": "une phrase d'accusation tabloïd",
  "exhibit": "citation entre « » tirée du wahala",
  "context": "2 lignes max de faits",
  "category": "Dating|Amitié|Famille|WhatsApp|Transport|Argent|Travail",
  "gravity": 1-10,
  "voice": {{
    "tone": "3-6 mots",
    "lexicon": ["mots"],
    "excuses": ["excuses"],
    "catchphrases": ["phrases"],
    "summary": "1 phrase vibe"
  }}
}}
"""
	return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def letter_messages(
	*,
	friend_name: str,
	case: dict[str, Any],
	people_vote: str,
	verdict: dict[str, Any],
) -> list[dict[str, str]]:
	system = """Tu écris une courte lettre WhatsApp à un pote après son procès Wahala Court.
Ton chaleureux, drôle, pas méchant. Français. Pas de jargon juridique lourd.
Réponds UNIQUEMENT en JSON: {"letter": "...", "opener": "salutation courte"}."""
	user = f"""Destinataire: {friend_name}
Charge: {case.get('charge')}
Pièce: {case.get('exhibit')}
Vote peuple: {people_vote}
Verdict tribunal: {verdict.get('headline')} — {verdict.get('sentence')}
Rationale: {verdict.get('rationale', '')}

Écris 4-7 lignes prêtes à coller dans WhatsApp, qui expliquent le contraste peuple vs tribunal.
"""
	return [{"role": "system", "content": system}, {"role": "user", "content": user}]
