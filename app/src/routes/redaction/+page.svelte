<script lang="ts">
	import { generatePosts, type GeneratedPosts } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import type { ArchiveEntry } from '$lib/data/model';
	import { VERDICT_LABEL } from '$lib/data/model';

	let selected = $state(0);
	let busy = $state(false);
	let error = $state('');
	let posts = $state<GeneratedPosts | null>(null);
	let cache = $state<Record<string, GeneratedPosts>>({});
	let copied = $state('');
	let genToken = 0;

	const entries = $derived(session.greffe);
	const entry = $derived<ArchiveEntry | null>(entries[selected] ?? null);

	async function ensurePosts(target: ArchiveEntry, force = false) {
		const key = target.caseFile.number;
		if (!force && cache[key]) {
			posts = cache[key];
			error = '';
			return;
		}
		const token = ++genToken;
		busy = true;
		error = '';
		posts = null;
		try {
			const res = await generatePosts({
				caseFile: {
					number: target.caseFile.number,
					charge: target.caseFile.charge,
					exhibit: target.caseFile.exhibit,
					context: target.caseFile.context,
					category: target.caseFile.category
				},
				verdict: {
					outcome: target.verdict.outcome,
					headline: target.verdict.headline,
					sentence: target.verdict.sentence,
					lawCite: target.verdict.lawCite
				},
				peopleShare: target.peopleShare
			});
			if (token !== genToken) return;
			cache = { ...cache, [key]: res };
			posts = res;
		} catch (e) {
			if (token !== genToken) return;
			error = e instanceof Error ? e.message : 'Erreur génération';
		} finally {
			if (token === genToken) busy = false;
		}
	}

	$effect(() => {
		const e = entry;
		if (!e) {
			posts = null;
			return;
		}
		void ensurePosts(e);
	});

	function pick(i: number) {
		selected = i;
	}

	async function copy(kind: keyof GeneratedPosts, text: string) {
		await navigator.clipboard.writeText(text);
		copied = kind;
		window.setTimeout(() => {
			if (copied === kind) copied = '';
		}, 1200);
	}

	function noteTitle(label: string) {
		return label.toLowerCase().replace(/\s+/g, '-');
	}
</script>

<section class="vault">
	<header class="vault__head">
		<p class="vault__path">greffe / rédaction</p>
		<h1 class="vault__title">Notes · affaires jugées</h1>
		<p class="vault__lead">
			Gemma rédige toute seule caption, WhatsApp et brouillon DEV — style vault, prêt à partager.
		</p>
	</header>

	{#if entries.length === 0}
		<p class="vault__empty">
			Aucune note encore. Passe une audience
			<a href="/debat">→ débat</a>
			puis vote — le greffe s’ouvre ici.
		</p>
	{:else}
		<div class="vault__layout">
			<aside class="vault__sidebar" aria-label="Affaires jugées">
				<p class="vault__side-label">[[affaires]]</p>
				{#each entries as e, i}
					<button
						type="button"
						class="vault__file"
						class:is-active={i === selected}
						onclick={() => pick(i)}
					>
						<span class="vault__file-icon" aria-hidden="true">✦</span>
						<span class="vault__file-body">
							<span class="vault__file-name">{e.caseFile.number}</span>
							<span class="vault__file-preview">{e.caseFile.charge}</span>
						</span>
						<span class="vault__file-tag">{VERDICT_LABEL[e.verdict.outcome]}</span>
					</button>
				{/each}
			</aside>

			<div class="vault__pane">
				{#if entry}
					<article class="vault__note vault__note--front">
						<p class="vault__meta">
							#{entry.caseFile.number} · peuple {entry.peopleShare}% ·
							{busy ? 'gemma écrit…' : 'auto'}
						</p>
						<h2 class="vault__note-title">{entry.caseFile.charge}</h2>
						<p class="vault__quote">« {entry.verdict.sentence} »</p>
						<p class="vault__props">
							<span>outcome:: {VERDICT_LABEL[entry.verdict.outcome]}</span>
							<span>law:: {entry.verdict.lawCite}</span>
						</p>
						{#if error}
							<p class="vault__err">{error} — backend FastAPI ?</p>
							<button class="vault__ghost" type="button" onclick={() => entry && void ensurePosts(entry, true)}>
								Réessayer
							</button>
						{:else if busy && !posts}
							<p class="vault__busy">Rédaction en cours…</p>
						{/if}
					</article>
				{/if}

				{#if posts}
					<div class="vault__stack">
						{#if posts.fallback}
							<p class="vault__hint">Mode fallback (pas de Gemma) — textes modèles.</p>
						{/if}
						{#each [
							{ key: 'caption', label: 'Caption partage', text: posts.caption },
							{ key: 'whatsapp', label: 'WhatsApp', text: posts.whatsapp },
							{ key: 'dev', label: 'Brouillon DEV', text: posts.dev }
						] as block}
							<section class="vault__note">
								<div class="vault__note-bar">
									<h3 class="vault__wikilink">[[{noteTitle(block.label)}]]</h3>
									<button
										type="button"
										class="vault__ghost"
										onclick={() => void copy(block.key as keyof GeneratedPosts, block.text)}
									>
										{copied === block.key ? 'copié' : 'copier'}
									</button>
								</div>
								<pre class="vault__md">{block.text}</pre>
							</section>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</section>
