/** API / WebSocket helpers for Wahala Court backend. */

import { PUBLIC_API_URL } from '$env/static/public';

const DEFAULT_HTTP = 'http://127.0.0.1:8000';

export function apiBase(): string {
	return (PUBLIC_API_URL || DEFAULT_HTTP).replace(/\/$/, '');
}

export function wsDebateUrl(): string {
	const base = apiBase();
	const u = new URL(base);
	u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:';
	u.pathname = '/ws/debate';
	u.search = '';
	u.hash = '';
	return u.toString();
}

export type DebateCase = {
	number: string;
	charge: string;
	exhibit: string;
	context: string;
	category: string;
};

export type DebateHistoryItem = { speaker: string; text: string };

export type DebateSource = {
	id?: string;
	title: string;
	url?: string | null;
	excerpt?: string;
	source?: string;
	score?: number;
};

export type DebateEvent =
	| { type: 'sources'; sources: DebateSource[] }
	| { type: 'typing'; speaker: string }
	| { type: 'token'; speaker: string; text: string }
	| {
			type: 'line';
			id: string;
			speaker: string;
			text: string;
			lawCite?: string | null;
			fallback?: boolean;
			npcCursor?: number;
	  }
	| { type: 'done'; npcCursor?: number }
	| { type: 'error'; message: string }
	| { type: 'pong' };

export type GeneratedPosts = {
	caption: string;
	whatsapp: string;
	dev: string;
	fallback?: boolean;
};

export type VoiceDNA = {
	tone: string;
	lexicon: string[];
	excuses: string[];
	catchphrases: string[];
	summary: string;
	fallback?: boolean;
};

export type ChamberResult = {
	procureur_closing: string;
	defense_closing: string;
	outcome: 'coupable' | 'innocent';
	headline: string;
	sentence: string;
	lawCite: string;
	dissent: string;
	wahalaScore: number;
	rationale: string;
	disagreesWithPeople: boolean;
	fallback: boolean;
	sources?: DebateSource[];
};

export type DepotResult = {
	caseFile: {
		number: string;
		accusedName: string;
		charge: string;
		exhibit: string;
		context: string;
		category: string;
		gravity?: number;
	};
	voice: VoiceDNA;
	friendName: string;
	fallback?: boolean;
};

export type FriendLetter = {
	opener: string;
	letter: string;
	fallback?: boolean;
};

export async function generatePosts(payload: {
	caseFile: Record<string, unknown>;
	verdict: Record<string, unknown>;
	peopleShare: number;
}): Promise<GeneratedPosts> {
	const res = await fetch(`${apiBase()}/v1/posts/generate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	if (!res.ok) throw new Error(`posts/generate ${res.status}`);
	return (await res.json()) as GeneratedPosts;
}

export async function deliberateChamber(payload: {
	case: DebateCase;
	transcript: DebateHistoryItem[];
	peopleVote: string;
	mode: string;
	voice?: VoiceDNA | null;
}): Promise<ChamberResult> {
	const res = await fetch(`${apiBase()}/v1/chamber/deliberate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	if (!res.ok) throw new Error(`chamber/deliberate ${res.status}`);
	return (await res.json()) as ChamberResult;
}

export async function extractVoice(payload: {
	raw: string;
	accusedName: string;
}): Promise<VoiceDNA> {
	const res = await fetch(`${apiBase()}/v1/voice/extract`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	if (!res.ok) throw new Error(`voice/extract ${res.status}`);
	return (await res.json()) as VoiceDNA;
}

export async function buildDepot(payload: {
	friendName: string;
	raw: string;
}): Promise<DepotResult> {
	const res = await fetch(`${apiBase()}/v1/depot/build`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	if (!res.ok) throw new Error(`depot/build ${res.status}`);
	return (await res.json()) as DepotResult;
}

export async function writeLetter(payload: {
	friendName: string;
	case: DebateCase & { accusedName?: string };
	peopleVote: string;
	verdict: Record<string, unknown>;
}): Promise<FriendLetter> {
	const res = await fetch(`${apiBase()}/v1/letter/write`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	if (!res.ok) throw new Error(`letter/write ${res.status}`);
	return (await res.json()) as FriendLetter;
}

/** Open debate WS, send one user turn, invoke onEvent until done. */
export function sendDebateTurn(opts: {
	role: string;
	text: string;
	case: DebateCase;
	history: DebateHistoryItem[];
	mode: string;
	npcCursor: number;
	voice?: VoiceDNA | null;
	onEvent: (ev: DebateEvent) => void;
	signal?: AbortSignal;
}): Promise<void> {
	return new Promise((resolve, reject) => {
		let settled = false;
		const ws = new WebSocket(wsDebateUrl());

		const finish = (err?: Error) => {
			if (settled) return;
			settled = true;
			try {
				ws.close();
			} catch {
				/* ignore */
			}
			if (err) reject(err);
			else resolve();
		};

		const onAbort = () => finish(new Error('aborted'));
		opts.signal?.addEventListener('abort', onAbort, { once: true });

		ws.onopen = () => {
			ws.send(
				JSON.stringify({
					type: 'user_message',
					role: opts.role,
					text: opts.text,
					case: opts.case,
					history: opts.history,
					mode: opts.mode,
					npcCursor: opts.npcCursor,
					voice: opts.voice ?? null
				})
			);
		};

		ws.onmessage = (e) => {
			try {
				const ev = JSON.parse(String(e.data)) as DebateEvent;
				opts.onEvent(ev);
				if (ev.type === 'done' || ev.type === 'error') {
					finish(ev.type === 'error' ? new Error(ev.message) : undefined);
				}
			} catch (err) {
				finish(err instanceof Error ? err : new Error(String(err)));
			}
		};

		ws.onerror = () => finish(new Error('WebSocket error'));
		ws.onclose = () => {
			if (!settled) finish();
		};
	});
}
