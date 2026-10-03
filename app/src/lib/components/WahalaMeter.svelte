<script lang="ts">
	import { session as defaultSession } from '$lib/stores/session.svelte';

	interface Props {
		session?: typeof defaultSession;
	}

	let { session = defaultSession }: Props = $props();
	const value = $derived(session.wahala);
</script>

<div class="wahala-meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={value} aria-label="Wahala meter">
	<div class="wahala-meter__bar" style:width="{value}%"></div>
	<span class="wahala-meter__label">WAHALA {value}%</span>
</div>
