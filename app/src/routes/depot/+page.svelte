<script lang="ts">
	import { goto } from '$app/navigation';
	import { buildDepot } from '$lib/api';
	import { session } from '$lib/stores/session.svelte';
	import type { CaseFile, Category } from '$lib/data/model';

	let friendName = $state('');
	let raw = $state('');
	let busy = $state(false);
	let error = $state('');
	let preview = $state<{ charge: string; exhibit: string; accusedName: string } | null>(null);

	async function deposit() {
		if (!raw.trim() || busy) return;
		busy = true;
		error = '';
		preview = null;
		try {
			const res = await buildDepot({
				friendName: friendName.trim() || 'LE POTE',
				raw: raw.trim()
			});
			const cats: Category[] = [
				'Dating',
				'Amitié',
				'Famille',
				'WhatsApp',
				'Transport',
				'Argent',
				'Travail'
			];
			const cat = cats.includes(res.caseFile.category as Category)
				? (res.caseFile.category as Category)
				: 'Amitié';
			const caseFile: CaseFile = {
				number: res.caseFile.number,
				accusedName: res.caseFile.accusedName,
				charge: res.caseFile.charge,
				exhibit: res.caseFile.exhibit,
				context: res.caseFile.context,
				category: cat,
				gravity: res.caseFile.gravity
			};
			session.applyDepot({
				caseFile,
				voice: res.voice,
				friendName: res.friendName
			});
			preview = {
				charge: caseFile.charge,
				exhibit: caseFile.exhibit,
				accusedName: caseFile.accusedName
			};
			goto('/role');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Dépôt impossible — backend down ?';
		} finally {
			busy = false;
		}
	}
</script>

<section class="depot">
	<header class="depot__head">
		<p class="depot__kicker">GREFFE · DÉPÔT DU POTE</p>
		<h1 class="depot__title">DÉPOSE LE WAHALA</h1>
		<p class="depot__lead">
			Colle les messages / le scoop. Gemma monte le dossier + l’ADN — tu choisis ton rôle, le tribunal joue le reste.
		</p>
	</header>

	<label class="depot__field">
		<span class="depot__label">Prénom du pote</span>
		<input
			class="depot__input"
			type="text"
			placeholder="ex. Kofi"
			bind:value={friendName}
			maxlength="40"
		/>
	</label>

	<label class="depot__field">
		<span class="depot__label">Messages / histoire</span>
		<textarea
			class="depot__area"
			rows="8"
			placeholder="Colle le thread WhatsApp ou raconte le wahala…"
			bind:value={raw}
		></textarea>
	</label>

	{#if error}
		<p class="depot__err">{error}</p>
	{/if}

	{#if preview}
		<p class="depot__ok">Dossier monté · {preview.accusedName} — {preview.charge}</p>
	{/if}

	<div class="depot__actions">
		<button class="btn btn--danger" type="button" disabled={!raw.trim() || busy} onclick={() => void deposit()}>
			{busy ? 'GREFFE EN COURS…' : 'DÉPOSER AU TRIBUNAL'}
		</button>
		<a class="depot__skip" href="/role">Passer · affaires du greffe →</a>
	</div>
</section>
