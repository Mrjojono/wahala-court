import type { TranscriptLine } from '$lib/data/model';
import { CASE_OF_THE_DAY } from '$lib/data/cases';

/** Script greffier (Acte 1) — zéro IA. */
export function greffierScript(charge: string, exhibit: string): string {
	return `LE TRIBUNAL DE WAHALA EST EN SESSION. Charge retenue : ${charge} Pièce à conviction : ${exhibit}`;
}

/** Répliques mock Acte 2 — prêt à être remplacées par Ollama + RAG. */
export const debateLines: TranscriptLine[] = [
	{
		id: 'l1',
		speaker: 'procureur',
		text: 'Le prévenu a trompé l’espérance collective. « 5 minutes » n’est pas une unité légale — c’est une escroquerie temporelle.',
		lawCite: 'Art. 312-A · Promesses mensongères entre amis'
	},
	{
		id: 'l2',
		speaker: 'defense',
		text: 'Objection culturelle ! Dans notre jurisprudence coutumière, « j’arrive » signifie « j’y pense très fort ».',
		lawCite: 'Art. 18 · Interprétation bienveillante du wahala'
	},
	{
		id: 'l3',
		speaker: 'accuse',
		text: CASE_OF_THE_DAY.exhibit.replace(/^«\s*|\s*»$/g, '') || 'Je jure que j’étais déjà dehors… mentalement.',
		lawCite: undefined
	},
	{
		id: 'l4',
		speaker: 'procureur',
		text: '47 minutes ! Le GPS, les bleus WhatsApp et le voisin témoignent. La Cour ne peut ignorer ces faits.',
		lawCite: 'Art. 94 · Preuve numérique irréfutable'
	},
	{
		id: 'l5',
		speaker: 'defense',
		text: 'Personne n’est mort. Un retard n’est pas un crime — c’est un sport national, Votre Honneur.',
		lawCite: 'Art. 2 · Proportionnalité des peines comiques'
	},
	{
		id: 'l6',
		speaker: 'juge',
		text: 'L’instruction est close. Le peuple vote. Ensuite la Cour tranche — avec ou sans pitié.',
		lawCite: 'Art. 1 · Ouverture de la délibération'
	}
];
