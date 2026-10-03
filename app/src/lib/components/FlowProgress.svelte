<script lang="ts">
	import { page } from '$app/state';
	import { FLOW_STEPS } from '$lib/data/model';
	import { session } from '$lib/stores/session.svelte';

	const path = $derived(page.url.pathname);
	const visible = $derived(
		FLOW_STEPS.some((s) => path === s.href || path.startsWith(s.href + '/')) ||
			path === '/verdict' ||
			path === '/redaction'
	);

	const activeIdx = $derived.by(() => {
		const i = FLOW_STEPS.findIndex((s) => path === s.href || path.startsWith(s.href + '/'));
		if (path === '/verdict' || path === '/redaction') return FLOW_STEPS.length - 1;
		return i;
	});
</script>

{#if visible && session.role}
	<nav class="flow-rail" aria-label="Progression de l’audience">
		{#each FLOW_STEPS as step, i}
			<span class="flow-rail__step" class:is-active={i === activeIdx} class:is-done={i < activeIdx}>
				{#if i < activeIdx}
					<a href={step.href}>{step.label}</a>
				{:else}
					{step.label}
				{/if}
			</span>
			{#if i < FLOW_STEPS.length - 1}
				<span class="flow-rail__sep" aria-hidden="true">·</span>
			{/if}
		{/each}
	</nav>
{/if}
