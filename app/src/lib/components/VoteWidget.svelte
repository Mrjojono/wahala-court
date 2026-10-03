<script lang="ts">
	import type { PeopleVote } from '$lib/data/model';
	import { session as defaultSession } from '$lib/stores/session.svelte';

	interface Props {
		session?: typeof defaultSession;
	}

	let { session = defaultSession }: Props = $props();

	function choose(choice: PeopleVote) {
		session.selectVote(choice);
	}
</script>

<div class="vote-widget" role="group" aria-label="Vote du public">
	<button
		type="button"
		class="vote-widget__option vote-widget__option--innocent"
		class:is-selected={session.vote === 'innocent'}
		onclick={() => choose('innocent')}
	>
		Innocent
	</button>
	<button
		type="button"
		class="vote-widget__option vote-widget__option--coupable"
		class:is-selected={session.vote === 'coupable'}
		onclick={() => choose('coupable')}
	>
		Coupable
	</button>
</div>
