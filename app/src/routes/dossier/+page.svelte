<script lang="ts">
	import { goto } from '$app/navigation';
	import { CATEGORY_LABEL } from '$lib/data/model';
	import { extractVoice } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import Persona from '$lib/components/Persona.svelte';
	import Stamp from '$lib/components/Stamp.svelte';

	const d = $derived(session.currentCase);
	let rawVoice = $state('');
	let extracting = $state(false);
	let voiceError = $state('');

	$effect(() => {
		if (!session.role) goto('/role');
	});

	function openAudience() {
		session.startCase();
		goto('/debat');
	}

	async function runExtract() {
		if (!rawVoice.trim() || extracting) return;
		extracting = true;
		voiceError = '';
		try {
			const dna = await extractVoice({ raw: rawVoice, accusedName: d.accusedName });
			session.setVoice(dna);
		} catch (e) {
			voiceError = e instanceof Error ? e.message : 'Erreur ADN';
		} finally {
			extracting = false;
		}
	}
</script>

<p class="dossier-page__back"><a href="/role">← CHANGER DE RÔLE</a></p>

<article class="folder folder--compact">
	<header class="folder__tab">
		<span>DOSSIER {d.number}</span>
		<span>{CATEGORY_LABEL[d.category]}</span>
	</header>

	<div class="folder__split">
		<aside class="polaroid polaroid--tight">
			<div class="polaroid__frame">
				<Persona who="accuse" size="fill" figure label={d.accusedName} />
			</div>
			<p class="polaroid__name">{d.accusedName}</p>
		</aside>

		<div class="folder__charge">
			<Stamp label="CHEF D'ACCUSATION" />
			<h1 class="folder__headline">{d.charge}</h1>
			<p class="folder__body">{d.context}</p>
			<aside class="sticky-note sticky-note--tight">
				<p class="sticky-note__kicker">PIÈCE À CONVICTION</p>
				<p class="sticky-note__quote">{d.exhibit}</p>
			</aside>
		</div>
	</div>

	{#if d.gravity != null}
		<div class="folder__stats folder__stats--one">
			<div class="folder__stat">
				<p class="folder__statLabel">GRAVITÉ</p>
				<p class="folder__statValue">{d.gravity} / 10</p>
			</div>
		</div>
	{/if}
</article>

<section class="voice-dna">
	<p class="voice-dna__kicker">ADN DU POTE · GEMMA</p>
	<p class="voice-dna__lead">
		Colle 3–5 messages WhatsApp de {d.accusedName}. Gemma en extrait le style — l’audience et la chambre
		parlent comme ton pote.
	</p>
	<textarea
		class="voice-dna__input"
		rows="4"
		placeholder="ex: frère j’arrive dans 5 min… wallah le trafic… je t’appelle juste après"
		bind:value={rawVoice}
	></textarea>
	<div class="voice-dna__row">
		<button class="btn" type="button" disabled={!rawVoice.trim() || extracting} onclick={() => void runExtract()}>
			{extracting ? 'EXTRACTION…' : 'EXTRAIRE L’ADN'}
		</button>
		{#if session.voice}
			<button class="btn" type="button" onclick={() => session.setVoice(null)}>EFFACER</button>
		{/if}
	</div>
	{#if voiceError}
		<p class="voice-dna__err">{voiceError}</p>
	{/if}
	{#if session.voice}
		<div class="voice-dna__card">
			<p class="voice-dna__tone">{session.voice.tone}</p>
			<p class="voice-dna__sum">{session.voice.summary}</p>
			{#if session.voice.lexicon?.length}
				<p class="voice-dna__tags">{session.voice.lexicon.join(' · ')}</p>
			{/if}
		</div>
	{/if}
</section>

<button class="btn btn--hero btn--danger" onclick={openAudience}>OUVRIR L'AUDIENCE →</button>
