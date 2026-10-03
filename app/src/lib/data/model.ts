/**
 * WAHALA COURT — Data Model (GDD)
 * Strict, exhaustif, prêt pour Ollama + RAG plus tard.
 */

// ── Personas / rôles ──────────────────────────────────────────────────────

export type PersonaName =
	| 'juge'
	| 'procureur'
	| 'defense'
	| 'accuse'
	| 'greffier'
	| 'temoin'
	| 'flat';

export type PlayerRole = 'juge' | 'procureur' | 'defense' | 'accuse';

export const PERSONA_LABEL: Record<PersonaName, string> = {
	juge: 'Le juge',
	procureur: 'Le procureur',
	defense: 'La défense',
	accuse: "L'accusé",
	greffier: 'Le greffier',
	temoin: 'Le témoin',
	flat: 'Le public'
};

export const PERSONA_ART: Record<PersonaName, string> = {
	juge: '/perso/juge.svg',
	procureur: '/perso/procureur.svg',
	defense: '/perso/defense.svg',
	accuse: '/perso/accuse.svg',
	greffier: '/perso/salle.svg',
	temoin: '/perso/temoin.svg',
	flat: '/perso/flat-a.svg'
};

/** Mur de casting : tous les SVG perso, collés, cliquables. */
export type CastingTile = {
	id: string;
	role: PlayerRole;
	title: string;
	blurb: string;
	note: string;
	cta: string;
	art: string;
};

/** Mur de casting — 4 rôles jouables d'origine. */
export const CASTING_WALL: CastingTile[] = [
	{
		id: 'juge',
		role: 'juge',
		title: 'LE JUGE',
		blurb: 'Vous siégez. Vous écoutez, vous tranchez.',
		note: 'PRÉSIDE',
		cta: 'PRENDRE LE SIÈGE',
		art: '/perso/juge.svg'
	},
	{
		id: 'procureur',
		role: 'procureur',
		title: 'LE PROCUREUR',
		blurb: 'Vous chargez. Vous voulez du sang — ou du thieb.',
		note: 'ACCUSE',
		cta: 'REQUÉRIR',
		art: '/perso/procureur.svg'
	},
	{
		id: 'defense',
		role: 'defense',
		title: 'LA DÉFENSE',
		blurb: 'Vous croyez en votre client, frigo vide ou pas.',
		note: 'PLAIDE',
		cta: 'PRENDRE LA PAROLE',
		art: '/perso/defense.svg'
	},
	{
		id: 'accuse',
		role: 'accuse',
		title: "L'ACCUSÉ",
		blurb: 'C’est votre dossier. La rumeur du couloir vous regarde.',
		note: 'BANC',
		cta: 'ENTRER AU BANC',
		art: '/perso/accuse.svg'
	}
];

export const ROLE_META = Object.fromEntries(CASTING_WALL.map((t) => [t.role, t])) as Record<
	PlayerRole,
	CastingTile
>;

// ── Dossier (format GDD §5) ───────────────────────────────────────────────

export type Category =
	| 'Dating'
	| 'Amitié'
	| 'Famille'
	| 'WhatsApp'
	| 'Transport'
	| 'Argent'
	| 'Travail';

export const CATEGORY_LABEL: Record<Category, string> = {
	Dating: 'Dating',
	Amitié: 'Amitié',
	Famille: 'Famille',
	WhatsApp: 'WhatsApp',
	Transport: 'Transport',
	Argent: 'Argent',
	Travail: 'Travail'
};

/** Une affaire = exactement le template GDD. */
export type CaseFile = {
	number: string;
	/** Charge tabloïd (1 phrase). */
	charge: string;
	/** Citation verbatim de l'ami. */
	exhibit: string;
	/** 2 lignes max. */
	context: string;
	category: Category;
	/** Nom affiché de l'accusé. */
	accusedName: string;
	/** Optionnel : gravité mock 0–10. */
	gravity?: number;
};

// ── Transcript / débat ────────────────────────────────────────────────────

export type TranscriptLine = {
	id: string;
	speaker: PersonaName;
	text: string;
	/** Article de loi cité (RAG ou mock). */
	lawCite?: string;
};

export type LawArticle = {
	code: string;
	article: string;
	texte: string;
};

// ── Vote & verdict ────────────────────────────────────────────────────────

export type PeopleVote = 'coupable' | 'innocent';

export type VerdictRecord = {
	outcome: PeopleVote;
	sealedBy: PersonaName;
	headline: string;
	/** Sentence comique du juge. */
	sentence: string;
	/** Article affiché (RAG / Gemma chambre). */
	lawCite: string;
	timestamp: number;
	/** Chambre du conseil Gemma */
	procureurClosing?: string;
	defenseClosing?: string;
	dissent?: string;
	rationale?: string;
	wahalaScore?: number;
	disagreesWithPeople?: boolean;
	chamberFallback?: boolean;
};

/** ADN stylistique du pote (extrait WhatsApp → Gemma). */
export type VoiceDNA = {
	tone: string;
	lexicon: string[];
	excuses: string[];
	catchphrases: string[];
	summary: string;
	fallback?: boolean;
};

export type ArchiveEntry = {
	caseFile: CaseFile;
	verdict: VerdictRecord;
	peopleShare: number;
};

// ── Moteur (mock → Ollama) ────────────────────────────────────────────────

export type TrialMode = 'chaos' | 'serieux';

export type EngineConfig = {
	model: string;
	ragEnabled: boolean;
	mode: TrialMode;
};

export const ENGINE_DEFAULT: EngineConfig = {
	model: 'gemma3:1b',
	ragEnabled: false, // passe true dès qu'une search TogoLM renvoie des sources
	mode: 'chaos'
};

export type Trial = {
	caseFile: CaseFile;
	transcript: TranscriptLine[];
	peopleVerdict: PeopleVote | null;
	verdict: VerdictRecord | null;
	archive: ArchiveEntry | null;
	engine: EngineConfig;
	role: PlayerRole | null;
};

export const VERDICT_LABEL: Record<PeopleVote, string> = {
	coupable: 'COUPABLE',
	innocent: 'NON COUPABLE'
};

export function verdictHeadline(trial: Trial): string {
	const people = trial.peopleVerdict;
	const court = trial.verdict?.outcome;
	if (!people || !court) return 'Le tribunal délibère…';
	const art = trial.verdict?.lawCite ?? 'Art. —';
	return `LE PEUPLE : ${VERDICT_LABEL[people]} — LE TRIBUNAL : ${VERDICT_LABEL[court]} (${art})`;
}

export const OBJECTION_LINES = [
	'Objection — pure mauvaise foi !',
	'Objection — le frigo n’a pas de mémoire !',
	'Objection — on ne juge pas sur un yaourt !',
	'Objection — ma cliente était en réunion Zoom !',
	'Objection — le thieb n’a pas de propriétaire absolu !'
] as const;

/** Qui peut lever une objection (adversaires seulement — pas le juge ni l’accusé). */
export const CAN_OBJECT: readonly PlayerRole[] = ['procureur', 'defense'];

export function canRaiseObjection(role: PlayerRole | null): boolean {
	return role != null && (CAN_OBJECT as readonly string[]).includes(role);
}

export const JUDGE_ON_OBJECTION = [
	'Objection retenue. La Cour note le wahala.',
	'Objection rejetée — continuez, maître.',
	'La Cour a entendu. Passez à autre chose.',
	'Objection partiellement retenue. Soyez brefs.'
] as const;

/** Étapes du parcours joueur (UI + garde-fous). */
export const FLOW_STEPS = [
	{ href: '/role', label: 'Rôle', id: 'role' },
	{ href: '/dossier', label: 'Dossier', id: 'dossier' },
	{ href: '/debat', label: 'Audience', id: 'debat' },
	{ href: '/vote', label: 'Vote', id: 'vote' },
	{ href: '/verdict', label: 'Verdict', id: 'verdict' }
] as const;

export const MIN_EXCHANGES_BEFORE_VOTE = 2;
export const OBJECTION_COOLDOWN_MS = 12_000;
export const OBJECTION_MAX_PER_TRIAL = 3;
