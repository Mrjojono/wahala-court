<script lang="ts">
	import { goto } from '$app/navigation';
	import { PERSONA_LABEL, MIN_EXCHANGES_BEFORE_VOTE, OBJECTION_MAX_PER_TRIAL } from '$lib/data/model';
	import { session } from '$lib/stores/session.svelte';
	import Persona from '$lib/components/Persona.svelte';
	import ObjectionBurst from '$lib/components/ObjectionBurst.svelte';

	let draft = $state('');
	let feedEl: HTMLDivElement | undefined = $state();
	let objBusy = $state(false);
	let objHint = $state('');

	const d = $derived(session.currentCase);
	const me = $derived(session.role ?? 'accuse');
	const need = $derived(Math.max(0, MIN_EXCHANGES_BEFORE_VOTE - session.exchangeCount));

	$effect(() => {
		if (!session.role) {
			goto('/role');
			return;
		}
		if (session.chat.length === 0) session.startCase();
	});

	$effect(() => {
		session.chat.length;
		session.streaming;
		queueMicrotask(() => {
			if (!feedEl) return;
			const nearBottom = feedEl.scrollHeight - feedEl.scrollTop - feedEl.clientHeight < 160;
			if (nearBottom) {
				feedEl.scrollTo({ top: feedEl.scrollHeight, behavior: 'smooth' });
			}
		});
	});

	async function send() {
		const text = draft;
		draft = '';
		await session.sendChat(text);
	}

	function onKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			void send();
		}
	}

	function object() {
		if (objBusy || !session.canObject) return;
		const ok = session.fireObjection();
		if (!ok) {
			objHint =
				session.objectionCount >= OBJECTION_MAX_PER_TRIAL
					? 'Plus d’objections pour cette audience.'
					: 'Patientez avant une nouvelle objection.';
			return;
		}
		objHint = '';
		objBusy = true;
		window.setTimeout(() => {
			objBusy = false;
		}, 12_000);
	}

	function speakerClass(speaker: string) {
		return `is-${speaker}`;
	}
</script>

<ObjectionBurst />

<section class="livechat">
	<header class="livechat__bar">
		<div class="livechat__identity">
			<p class="livechat__meta">{d.number}</p>
			<p class="livechat__title">AUDIENCE</p>
			<p class="livechat__you">Vous · {PERSONA_LABEL[me]}</p>
		</div>
		<div class="livechat__tools">
			<span class="livechat__wahala" title="Niveau de wahala">⚡ {session.wahala}%</span>
			<button
				type="button"
				class="livechat__mode"
				class:is-chaos={session.engine.mode === 'chaos'}
				onclick={() => session.setMode(session.engine.mode === 'chaos' ? 'serieux' : 'chaos')}
			>
				{session.engine.mode === 'chaos' ? 'CHAOS' : 'SÉRIEUX'}
			</button>
		</div>
	</header>

	<p class="livechat__hint">
		{#if need > 0}
			Encore {need} échange{need > 1 ? 's' : ''} avant le vote du peuple.
		{:else}
			Assez entendu — vous pouvez ouvrir le vote.
		{/if}
		{#if session.canObject}
			· Objection : défense / procureur ({session.objectionCount}/{OBJECTION_MAX_PER_TRIAL})
		{:else if me === 'juge'}
			· Vous présidez — pas d’objection, vous tranchez.
		{:else}
			· Accusé : plaidez, pas d’objection (c’est pour les avocats).
		{/if}
	</p>

	<div class="livechat__feed" bind:this={feedEl} aria-live="polite">
		{#each session.chat as line (line.id)}
			<article
				class="livechat__msg {speakerClass(line.speaker)}"
				class:is-mine={line.speaker === me}
				class:is-clerk={line.speaker === 'greffier'}
				class:is-objection={line.text.toLowerCase().startsWith('objection')}
			>
				{#if line.speaker !== 'greffier'}
					<Persona who={line.speaker} size="sm" />
				{/if}
				<div class="livechat__copy">
					<p class="livechat__who">{PERSONA_LABEL[line.speaker]}</p>
					<p class="livechat__text">{line.text}</p>
					{#if line.lawCite}
						<p class="livechat__cite">{line.lawCite}</p>
					{/if}
				</div>
			</article>
		{/each}

		{#if session.streaming && session.typingSpeaker}
			<p class="livechat__typing">
				<span class="livechat__dots" aria-hidden="true"></span>
				{PERSONA_LABEL[session.typingSpeaker]} prend la parole…
			</p>
		{/if}
	</div>

	<footer class="livechat__dock">
		{#if session.lastSources.length > 0}
			<details class="livechat__sources">
				<summary>Sources TogoLM · {session.lastSources.length}</summary>
				<ul>
					{#each session.lastSources.slice(0, 3) as src}
						<li>
							{#if src.url}
								<a href={src.url} target="_blank" rel="noreferrer">{src.title}</a>
							{:else}
								{src.title}
							{/if}
						</li>
					{/each}
				</ul>
			</details>
		{/if}

		{#if objHint}
			<p class="livechat__obj-hint">{objHint}</p>
		{/if}

		<form
			class="livechat__form"
			onsubmit={(e) => {
				e.preventDefault();
				void send();
			}}
		>
			<textarea
				class="livechat__input"
				rows="2"
				placeholder="Réplique en tant que {PERSONA_LABEL[me]}… (Entrée pour envoyer)"
				bind:value={draft}
				onkeydown={onKey}
				disabled={session.streaming}
			></textarea>
			<div class="livechat__actions">
				{#if session.canObject}
					<button
						class="btn livechat__obj-btn"
						type="button"
						disabled={objBusy || session.streaming || session.objectionCount >= OBJECTION_MAX_PER_TRIAL}
						onclick={object}
					>
						{objBusy ? '…' : 'OBJECTION !'}
					</button>
				{/if}
				<button class="btn" type="submit" disabled={!draft.trim() || session.streaming}>
					{session.streaming ? '…' : 'ENVOYER'}
				</button>
				<button
					class="btn btn--danger"
					type="button"
					onclick={() => goto('/vote')}
					disabled={!session.canCloseDebate || session.streaming}
				>
					VOTER
				</button>
			</div>
		</form>
	</footer>
</section>
