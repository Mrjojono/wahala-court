<script lang="ts">
	import { goto } from '$app/navigation';
	import { session } from '$lib/stores/session.svelte';
	import AlertStripe from '$lib/components/AlertStripe.svelte';
	import Stamp from '$lib/components/Stamp.svelte';
	import PollBar from '$lib/components/PollBar.svelte';
	import type { PeopleVote } from '$lib/data/model';

	$effect(() => {
		if (!session.role) goto('/role');
	});

	const d = $derived(session.currentCase);
	const poll = $derived(
		session.vote === 'coupable'
			? { guilty: 72, innocent: 28 }
			: session.vote === 'innocent'
				? { guilty: 41, innocent: 59 }
				: { guilty: 64, innocent: 36 }
	);

	function choose(choice: PeopleVote) {
		session.selectVote(choice);
	}

	async function confirm() {
		if (!session.vote || session.deliberating) return;
		await session.submitVoteWithChamber();
		goto('/verdict');
	}
</script>

<AlertStripe text="INTERRUPTION D'AUDIENCE // VOTE DU PEUPLE" />

<header class="vote-page__head">
	<div>
		<p class="vote-page__matter">{d.number} · {d.accusedName}</p>
		<h1 class="vote-page__title">LE TRIBUNAL DÉLIBÈRE</h1>
	</div>
	<Stamp label="SILENCE DANS LA SALLE" tone="gold" tilt />
</header>

<p class="vote-page__lede">{d.charge}</p>

<div class="vote-duel" role="group" aria-label="Choix du jury">
	<button
		type="button"
		class="vote-duel__btn vote-duel__btn--guilty"
		class:is-selected={session.vote === 'coupable'}
		onclick={() => choose('coupable')}
		disabled={session.deliberating}
	>
		<span class="vote-duel__main">COUPABLE</span>
		<span class="vote-duel__sub">// GUILTY</span>
	</button>
	<button
		type="button"
		class="vote-duel__btn vote-duel__btn--innocent"
		class:is-selected={session.vote === 'innocent'}
		onclick={() => choose('innocent')}
		disabled={session.deliberating}
	>
		<span class="vote-duel__main">NON COUPABLE</span>
		<span class="vote-duel__sub">// ACQUIT</span>
	</button>
</div>

<PollBar guilty={poll.guilty} innocent={poll.innocent} />

{#if session.deliberating}
	<p class="vote-page__chamber" aria-live="polite">
		CHAMBRE DU CONSEIL GEMMA — procureur · défense · juge délibèrent…
	</p>
{/if}

<button
	class="btn btn--hero"
	onclick={() => void confirm()}
	disabled={!session.vote || session.deliberating}
>
	{session.deliberating ? 'DÉLIBÉRATION…' : 'CONFIRMER MON VOTE'}
</button>
