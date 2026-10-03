"""Mock debate lines when Ollama is unavailable."""

from __future__ import annotations

MOCK_LINES: list[dict[str, str]] = [
	{
		"speaker": "procureur",
		"text": "Le prévenu a trompé l'espérance collective. « 5 minutes » n'est pas une unité légale — c'est une escroquerie temporelle.",
		"lawCite": "Art. 312-A · Promesses mensongères entre amis",
	},
	{
		"speaker": "defense",
		"text": "Objection culturelle ! Dans notre jurisprudence coutumière, « j'arrive » signifie « j'y pense très fort ».",
		"lawCite": "Art. 18 · Interprétation bienveillante du wahala",
	},
	{
		"speaker": "accuse",
		"text": "Je jure que j'étais déjà dehors… mentalement.",
		"lawCite": "",
	},
	{
		"speaker": "procureur",
		"text": "Les bleus WhatsApp et le voisin témoignent. La Cour ne peut ignorer ces faits.",
		"lawCite": "Art. 94 · Preuve numérique irréfutable",
	},
	{
		"speaker": "defense",
		"text": "Personne n'est mort. Un retard n'est pas un crime — c'est un sport national, Votre Honneur.",
		"lawCite": "Art. 2 · Proportionnalité des peines comiques",
	},
	{
		"speaker": "juge",
		"text": "L'instruction est close. Le peuple vote. Ensuite la Cour tranche — avec ou sans pitié.",
		"lawCite": "Art. 1 · Ouverture de la délibération",
	},
]


def next_mock(player_role: str, cursor: int) -> tuple[dict[str, str] | None, int]:
	i = cursor
	while i < len(MOCK_LINES):
		line = MOCK_LINES[i]
		i += 1
		if line["speaker"] != player_role:
			return line, i
	return None, i
