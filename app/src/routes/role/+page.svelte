<script lang="ts">
	import { goto } from '$app/navigation';
	import { CASTING_WALL, type PlayerRole } from '$lib/data/model';
	import { session } from '$lib/stores/session.svelte';

	function choose(role: PlayerRole) {
		session.chooseRole(role);
		goto('/dossier');
	}
</script>

<section class="cast">
	<p class="cast__eyebrow">ÉTAPE 1 · CHOISISSEZ VOTRE RÔLE</p>
	<div class="cast__gallery">
		{#each CASTING_WALL as tile}
			<button type="button" class="cast__shot" onclick={() => choose(tile.role)}>
				<img class="cast__img" src={tile.art} alt={tile.title} />
				<span class="cast__veil" aria-hidden="true"></span>
				<span class="cast__label">
					<span class="cast__note">{tile.note}</span>
					<span class="cast__name">{tile.title}</span>
					<span class="cast__blurb">{tile.blurb}</span>
					<span class="cast__cta">{tile.cta}</span>
				</span>
			</button>
		{/each}
	</div>
</section>
