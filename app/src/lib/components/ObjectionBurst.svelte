<script lang="ts">
	import { session } from '$lib/stores/session.svelte';
</script>

{#if session.objectionFlash}
	<div class="objection" role="status" aria-live="assertive">
		<span class="objection__stamp">{session.objectionFlash}</span>
	</div>
{/if}
