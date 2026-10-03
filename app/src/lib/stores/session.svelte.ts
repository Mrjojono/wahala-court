import { CASES } from '$lib/data/cases';
import { debateLines, greffierScript } from '$lib/data/trial';
import { deliberateChamber, sendDebateTurn, type DebateSource } from '$lib/api';
import {
	ENGINE_DEFAULT,
	JUDGE_ON_OBJECTION,
	MIN_EXCHANGES_BEFORE_VOTE,
	OBJECTION_COOLDOWN_MS,
	OBJECTION_LINES,
	OBJECTION_MAX_PER_TRIAL,
	canRaiseObjection,
	type ArchiveEntry,
	type CaseFile,
	type EngineConfig,
	type PeopleVote,
	type PersonaName,
	type PlayerRole,
	type TranscriptLine,
	type VerdictRecord,
	type VoiceDNA
} from '$lib/data/model';

function createSession() {
	let caseIndex = $state(0);
	let pendingVote = $state<PeopleVote | null>(null);
	let peopleVerdict = $state<PeopleVote | null>(null);
	let verdict = $state<VerdictRecord | null>(null);
	let greffe = $state<ArchiveEntry[]>([]);
	let role = $state<PlayerRole | null>(null);
	let engine = $state<EngineConfig>({ ...ENGINE_DEFAULT });
	let objectionFlash = $state<string | null>(null);
	let started = $state(false);
	let chat = $state<TranscriptLine[]>([]);
	let npcCursor = $state(0);
	let streaming = $state(false);
	let typingSpeaker = $state<PersonaName | null>(null);
	let lastSources = $state<DebateSource[]>([]);
	let streamBuf = $state('');
	let voice = $state<VoiceDNA | null>(null);
	let deliberating = $state(false);
	let objectionCount = $state(0);
	let lastObjectionAt = $state(0);
	let customCase = $state<CaseFile | null>(null);
	let friendName = $state('');
	let friendLetter = $state('');

	const currentCase = $derived<CaseFile>(customCase ?? CASES[caseIndex % CASES.length]);
	const wahala = $derived(
		verdict?.wahalaScore != null
			? verdict.wahalaScore
			: Math.min(100, Math.round(chat.length * 11 + objectionCount * 8))
	);
	const exchangeCount = $derived(chat.filter((m) => m.speaker !== 'greffier').length);
	const canCloseDebate = $derived(exchangeCount >= MIN_EXCHANGES_BEFORE_VOTE);
	const canObject = $derived(canRaiseObjection(role));
	const objectionReady = $derived(
		canObject &&
			!streaming &&
			objectionCount < OBJECTION_MAX_PER_TRIAL &&
			Date.now() - lastObjectionAt >= OBJECTION_COOLDOWN_MS
	);
	const objectionCooldownLeft = $derived(
		Math.max(0, OBJECTION_COOLDOWN_MS - (Date.now() - lastObjectionAt))
	);

	function seedChat() {
		const c = customCase ?? CASES[caseIndex % CASES.length];
		chat = [
			{
				id: 'greffier-open',
				speaker: 'greffier',
				text: greffierScript(c.charge, c.exhibit)
			}
		];
		npcCursor = 0;
		lastSources = [];
		streamBuf = '';
		typingSpeaker = null;
	}

	function startCase() {
		started = true;
		pendingVote = null;
		peopleVerdict = null;
		verdict = null;
		objectionFlash = null;
		streaming = false;
		deliberating = false;
		objectionCount = 0;
		lastObjectionAt = 0;
		seedChat();
	}

	function chooseRole(next: PlayerRole) {
		role = next;
		startCase();
	}

	function setVoice(next: VoiceDNA | null) {
		voice = next;
	}

	function applyDepot(payload: {
		caseFile: CaseFile;
		voice?: VoiceDNA | null;
		friendName?: string;
	}) {
		customCase = payload.caseFile;
		if (payload.voice) voice = payload.voice;
		if (payload.friendName) friendName = payload.friendName;
		started = false;
		verdict = null;
		peopleVerdict = null;
		pendingVote = null;
		friendLetter = '';
	}

	function setFriendLetter(text: string) {
		friendLetter = text;
	}

	function clearCustomCase() {
		customCase = null;
		friendName = '';
		friendLetter = '';
	}

	function pushMockNpc(speaker: PlayerRole) {
		if (npcCursor >= debateLines.length) return;
		let next = debateLines[npcCursor];
		let guard = 0;
		while (next && next.speaker === speaker && npcCursor + guard < debateLines.length - 1) {
			guard += 1;
			next = debateLines[npcCursor + guard];
		}
		npcCursor = Math.min(debateLines.length, npcCursor + guard + 1);
		if (next) {
			chat = [
				...chat,
				{
					...next,
					id: `npc-${Date.now()}`
				}
			];
		}
	}

	async function sendChat(raw: string) {
		const text = raw.trim();
		if (!text || streaming) return;
		const speaker = role ?? 'accuse';
		const history = chat
			.filter((m) => m.speaker !== 'greffier')
			.map((m) => ({ speaker: m.speaker, text: m.text }));

		chat = [
			...chat,
			{
				id: `u-${Date.now()}`,
				speaker,
				text
			}
		];

		streaming = true;
		typingSpeaker = null;
		streamBuf = '';
		let draftId = `stream-${Date.now()}`;

		try {
			await sendDebateTurn({
				role: speaker,
				text,
				case: {
					number: currentCase.number,
					charge: currentCase.charge,
					exhibit: currentCase.exhibit,
					context: currentCase.context,
					category: currentCase.category
				},
				history,
				mode: engine.mode,
				npcCursor,
				voice,
				onEvent: (ev) => {
					if (ev.type === 'sources') {
						lastSources = ev.sources ?? [];
						engine = { ...engine, ragEnabled: (ev.sources?.length ?? 0) > 0 };
					} else if (ev.type === 'typing') {
						typingSpeaker = (ev.speaker as PersonaName) || null;
						streamBuf = '';
						draftId = `stream-${Date.now()}-${ev.speaker}`;
						chat = [
							...chat,
							{
								id: draftId,
								speaker: (ev.speaker as PersonaName) || 'procureur',
								text: '…'
							}
						];
					} else if (ev.type === 'token') {
						streamBuf += ev.text;
						const id = draftId;
						chat = chat.map((m) =>
							m.id === id
								? {
										...m,
										speaker: (ev.speaker as PersonaName) || m.speaker,
										text: streamBuf
									}
								: m
						);
					} else if (ev.type === 'line') {
						typingSpeaker = null;
						const cite = ev.lawCite || undefined;
						const id = draftId;
						chat = chat.map((m) =>
							m.id === id
								? {
										id: ev.id || id,
										speaker: (ev.speaker as PersonaName) || m.speaker,
										text: ev.text,
										lawCite: cite
									}
								: m
						);
						if (!chat.some((m) => m.id === id || m.id === ev.id)) {
							chat = [
								...chat,
								{
									id: ev.id,
									speaker: ev.speaker as PersonaName,
									text: ev.text,
									lawCite: cite
								}
							];
						}
						if (typeof ev.npcCursor === 'number') npcCursor = ev.npcCursor;
						streamBuf = '';
					} else if (ev.type === 'done') {
						if (typeof ev.npcCursor === 'number') npcCursor = ev.npcCursor;
					}
				}
			});
		} catch {
			chat = chat.filter((m) => !m.id.startsWith('stream-'));
			pushMockNpc(speaker);
		} finally {
			streaming = false;
			typingSpeaker = null;
			streamBuf = '';
		}
	}

	function selectVote(choice: PeopleVote) {
		pendingVote = choice;
	}

	function applyChamberToVerdict(
		people: PeopleVote,
		chamber: Awaited<ReturnType<typeof deliberateChamber>>
	): VerdictRecord {
		const record: VerdictRecord = {
			outcome: chamber.outcome,
			sealedBy: 'juge',
			headline: chamber.headline,
			sentence: chamber.sentence,
			lawCite: chamber.lawCite,
			timestamp: Date.now(),
			procureurClosing: chamber.procureur_closing,
			defenseClosing: chamber.defense_closing,
			dissent: chamber.dissent,
			rationale: chamber.rationale,
			wahalaScore: chamber.wahalaScore,
			disagreesWithPeople: chamber.disagreesWithPeople,
			chamberFallback: chamber.fallback
		};
		verdict = record;
		peopleVerdict = people;
		const peopleShare = people === 'coupable' ? 78 : 34;
		const entry: ArchiveEntry = {
			caseFile: currentCase,
			verdict: record,
			peopleShare
		};
		if (!greffe.some((g) => g.caseFile.number === entry.caseFile.number)) {
			greffe = [entry, ...greffe];
		}
		return record;
	}

	function renderVerdict(): VerdictRecord {
		const people = peopleVerdict ?? pendingVote ?? 'coupable';
		peopleVerdict = people;
		const record: VerdictRecord = {
			outcome: people,
			sealedBy: 'juge',
			headline: people === 'coupable' ? 'COUPABLE' : 'NON COUPABLE',
			sentence:
				people === 'coupable'
					? 'Deux semaines de nettoyage du micro-ondes et interdiction d’approcher le frigo du 3ème.'
					: 'Acquittement avec avertissement solennel : le temps des autres n’est pas une ressource illimitée.',
			lawCite: 'Art. 419-B · Crimes de pause & promesses',
			timestamp: Date.now(),
			chamberFallback: true
		};
		verdict = record;
		const peopleShare = people === 'coupable' ? 78 : 34;
		const entry: ArchiveEntry = {
			caseFile: currentCase,
			verdict: record,
			peopleShare
		};
		if (!greffe.some((g) => g.caseFile.number === entry.caseFile.number)) {
			greffe = [entry, ...greffe];
		}
		return record;
	}

	async function submitVoteWithChamber(): Promise<VerdictRecord> {
		if (!pendingVote) throw new Error('no vote');
		const people = pendingVote;
		peopleVerdict = people;
		deliberating = true;
		try {
			const chamber = await deliberateChamber({
				case: {
					number: currentCase.number,
					charge: currentCase.charge,
					exhibit: currentCase.exhibit,
					context: currentCase.context,
					category: currentCase.category
				},
				transcript: chat.map((m) => ({ speaker: m.speaker, text: m.text })),
				peopleVote: people,
				mode: engine.mode,
				voice
			});
			if (chamber.sources?.length) {
				lastSources = chamber.sources;
				engine = { ...engine, ragEnabled: true };
			}
			return applyChamberToVerdict(people, chamber);
		} catch {
			return renderVerdict();
		} finally {
			deliberating = false;
		}
	}

	function submitVote() {
		void submitVoteWithChamber();
	}

	function nextCase() {
		customCase = null;
		friendName = '';
		friendLetter = '';
		caseIndex = (caseIndex + 1) % CASES.length;
		startCase();
	}

	function selectCase(index: number) {
		customCase = null;
		friendName = '';
		friendLetter = '';
		caseIndex = ((index % CASES.length) + CASES.length) % CASES.length;
		startCase();
	}

	function replay(entry: ArchiveEntry) {
		const idx = CASES.findIndex((c) => c.number === entry.caseFile.number);
		if (idx >= 0) caseIndex = idx;
		peopleVerdict = entry.verdict.outcome;
		pendingVote = entry.verdict.outcome;
		verdict = entry.verdict;
		started = true;
		seedChat();
	}

	function fireObjection(): boolean {
		if (!canRaiseObjection(role) || streaming) return false;
		if (objectionCount >= OBJECTION_MAX_PER_TRIAL) return false;
		if (Date.now() - lastObjectionAt < OBJECTION_COOLDOWN_MS) return false;

		const speaker = role as PlayerRole;
		const line = OBJECTION_LINES[Math.floor(Math.random() * OBJECTION_LINES.length)];
		const ruling = JUDGE_ON_OBJECTION[Math.floor(Math.random() * JUDGE_ON_OBJECTION.length)];
		objectionFlash = line;
		lastObjectionAt = Date.now();
		objectionCount += 1;
		chat = [
			...chat,
			{ id: `obj-${Date.now()}`, speaker, text: line },
			{
				id: `obj-juge-${Date.now()}`,
				speaker: 'juge',
				text: ruling,
				lawCite: 'Art. 9 · Incident d’audience'
			}
		];
		window.setTimeout(() => {
			if (objectionFlash === line) objectionFlash = null;
		}, 1600);
		return true;
	}

	function setMode(mode: EngineConfig['mode']) {
		engine = { ...engine, mode };
	}

	return {
		get currentCase() {
			return currentCase;
		},
		get debate() {
			return { index: npcCursor, lines: chat };
		},
		get chat() {
			return chat;
		},
		get canCloseDebate() {
			return canCloseDebate;
		},
		get exchangeCount() {
			return exchangeCount;
		},
		get canObject() {
			return canObject;
		},
		get objectionReady() {
			return objectionReady;
		},
		get objectionCount() {
			return objectionCount;
		},
		get objectionCooldownLeft() {
			return objectionCooldownLeft;
		},
		get vote() {
			return pendingVote;
		},
		get peopleVerdict() {
			return peopleVerdict;
		},
		get verdict() {
			return verdict;
		},
		get greffe() {
			return greffe;
		},
		get wahala() {
			return wahala;
		},
		get role() {
			return role;
		},
		get engine() {
			return engine;
		},
		get objectionFlash() {
			return objectionFlash;
		},
		get started() {
			return started;
		},
		get streaming() {
			return streaming;
		},
		get typingSpeaker() {
			return typingSpeaker;
		},
		get lastSources() {
			return lastSources;
		},
		get voice() {
			return voice;
		},
		get friendName() {
			return friendName;
		},
		get friendLetter() {
			return friendLetter;
		},
		get hasCustomCase() {
			return customCase != null;
		},
		get deliberating() {
			return deliberating;
		},
		startCase,
		chooseRole,
		sendChat,
		selectVote,
		submitVote,
		submitVoteWithChamber,
		renderVerdict,
		nextCase,
		selectCase,
		replay,
		fireObjection,
		setMode,
		setVoice,
		applyDepot,
		setFriendLetter,
		clearCustomCase
	};
}

export const session = createSession();
