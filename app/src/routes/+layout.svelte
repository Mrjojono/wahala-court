<script lang="ts">
	import '../styles/index.scss';
	import FloatingNav from '$lib/components/FloatingNav.svelte';
	import FlowProgress from '$lib/components/FlowProgress.svelte';
	import { page } from '$app/state';

	let { children } = $props();

	const path = $derived(page.url.pathname);
	const flush = $derived(path === '/role' || path === '/debat');
</script>

<div class="screen" class:screen--flush={flush}>
	<main class="screen__body" class:screen__body--flush={flush}>
		<FlowProgress />
		{@render children()}
	</main>
	<FloatingNav />
</div>
