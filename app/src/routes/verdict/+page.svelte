<script lang="ts">
	import { goto } from '$app/navigation';
	import { VERDICT_LABEL, verdictHeadline, ENGINE_DEFAULT, type Trial } from '$lib/data/model';
	import { writeLetter } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import Persona from '$lib/components/Persona.svelte';
	import Stamp from '$lib/components/Stamp.svelte';
	import PollBar from '$lib/components/PollBar.svelte';
	import AlertStripe from '$lib/components/AlertStripe.svelte';

	let letterBusy = $state(false);
	let letterErr = $state('');
	let letterTried = $state(false);
	let copied = $state(false);

	$effect(() => {
		if (!session.verdict && !session.deliberating) session.renderVerdict();
	});

	$effect(() => {
		const v = session.verdict;
		const name = session.friendName;
		if (!v || !name || session.friendLetter || letterBusy || letterTried) return;
		letterTried = true;
		letterBusy = true;
		letterErr = '';
		void writeLetter({
			friendName: name,
			case: {
				number: session.currentCase.number,
				charge: session.currentCase.charge,
				exhibit: session.currentCase.exhibit,
				context: session.currentCase.context,
				category: session.currentCase.category,
				accusedName: session.currentCase.accusedName
			},
			peopleVote: session.peopleVerdict ?? session.vote ?? 'coupable',
			verdict: {
				outcome: v.outcome,
				headline: v.headline,
				sentence: v.sentence,
				lawCite: v.lawCite,
				rationale: v.rationale ?? ''
			}
		})
			.then((res) => session.setFriendLetter(res.letter))
			.catch((e) => {
				letterErr = e instanceof Error ? e.message : 'Lettre impossible';
			})
			.finally(() => {
				letterBusy = false;
			});
	});

	const verdict = $derived(session.verdict);
	const people = $derived(session.peopleVerdict ?? session.vote ?? 'coupable');
	const guiltyPct = $derived(people === 'coupable' ? 78 : 22);
	const innocentPct = $derived(100 - guiltyPct);
	const archive = $derived(session.greffe[0]);
	const clash = $derived(!!verdict?.disagreesWithPeople);

	const trial = $derived.by((): Trial | null => {
		if (!verdict) return null;
		return {
			caseFile: session.currentCase,
			transcript: session.debate.lines,
			peopleVerdict: people,
			verdict,
			archive: archive ?? null,
			engine: session.engine ?? ENGINE_DEFAULT,
			role: session.role
		};
	});

	function nextCase() {
		session.nextCase();
		goto('/dossier');
	}

	async function shareCard() {
		if (!trial || !verdict) return;
		const text = `${verdictHeadline(trial)}\n${verdict.sentence}\n${verdict.rationale ?? ''}\n— Wahala Court · Chambre Gemma`;
		if (navigator.share) {
			await navigator.share({ title: 'Wahala Court', text });
			return;
		}
		await navigator.clipboard.writeText(text);
	}

	async function copyLetter() {
		if (!session.friendLetter) return;
		await navigator.clipboard.writeText(session.friendLetter);
		copied = true;
		window.setTimeout(() => (copied = false), 1200);
	}
</script>

{#if verdict && trial}
	<AlertStripe
		text={clash
			? 'FLASH · PEUPLE ≠ TRIBUNAL GEMMA'
			: 'FLASH SPÉCIAL · VERDICT'}
		tone="ink"
	/>

	<h1 class="verdict-page__title">LE VERDICT EST TOMBÉ</h1>
	<p class="verdict-page__sub">{verdictHeadline(trial)}</p>

	<div class="verdict-grid">
		<section class="verdict-card verdict-card--people">
			<p class="verdict-card__eyebrow">LE PEUPLE</p>
			<p class="verdict-card__pct">{guiltyPct}%</p>
			<p class="verdict-card__claim">{VERDICT_LABEL[people]}</p>
			<PollBar guilty={guiltyPct} innocent={innocentPct} />
		</section>

		<section class="verdict-card verdict-card--tribunal">
			<p class="verdict-card__eyebrow">LE TRIBUNAL · GEMMA</p>
			<div class="verdict-card__row">
				<Persona who="juge" size="md" figure />
				<div>
					<p class="verdict-card__claim">{VERDICT_LABEL[verdict.outcome]}</p>
					<p class="verdict-card__law">{verdict.lawCite}</p>
				</div>
			</div>
			<Stamp label={clash ? 'DISSIDENCE' : 'SCELLÉ'} tone="gold" tilt />
		</section>
	</div>

	{#if verdict.procureurClosing || verdict.defenseClosing}
		<section class="chamber-minutes">
			<p class="chamber-minutes__label">PROCÈS-VERBAL · CHAMBRE DU CONSEIL</p>
			{#if verdict.procureurClosing}
				<p class="chamber-minutes__line"><strong>Procureur —</strong> {verdict.procureurClosing}</p>
			{/if}
			{#if verdict.defenseClosing}
				<p class="chamber-minutes__line"><strong>Défense —</strong> {verdict.defenseClosing}</p>
			{/if}
			{#if verdict.rationale}
				<p class="chamber-minutes__line chamber-minutes__line--rationale">{verdict.rationale}</p>
			{/if}
			{#if verdict.dissent}
				<p class="chamber-minutes__line chamber-minutes__line--dissent">Note : {verdict.dissent}</p>
			{/if}
		</section>
	{/if}

	<section class="sentence sentence--compact">
		<p class="sentence__label">SENTENCE</p>
		<p class="sentence__text">« {verdict.sentence} »</p>
		<Stamp label="SANS SURSIS" />
	</section>

	{#if session.friendName}
		<section class="friend-letter">
			<p class="friend-letter__kicker">LETTRE AU POTE · {session.friendName}</p>
			{#if letterBusy && !session.friendLetter}
				<p class="friend-letter__busy">Gemma rédige…</p>
			{:else if session.friendLetter}
				<pre class="friend-letter__body">{session.friendLetter}</pre>
				<button class="btn" type="button" onclick={() => void copyLetter()}>
					{copied ? 'COPIÉ' : 'COPIER LA LETTRE'}
				</button>
			{:else if letterErr}
				<p class="friend-letter__err">{letterErr}</p>
			{/if}
		</section>
	{/if}

	<div class="verdict-page__actions">
		<button class="btn" type="button" onclick={shareCard}>PARTAGER</button>
		<button class="btn" type="button" onclick={() => goto('/redaction')}>RÉDIGER LE POST</button>
		<button class="btn btn--danger" onclick={nextCase}>AFFAIRE SUIVANTE →</button>
	</div>
{/if}
