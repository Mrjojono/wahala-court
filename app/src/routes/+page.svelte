<script lang="ts">
	import { goto } from '$app/navigation';
	import Steps from '$lib/components/Steps.svelte';
	import { session } from '$lib/stores/session.svelte';

	function enter() {
		session.startCase();
		goto('/role');
	}
</script>

<header class="accueil__top">
	<a class="accueil__logo" href="/">WAHALA COURT</a>
	<p class="accueil__links">
		<a href="/depot">DÉPÔT</a>
		·
		<a href="/regles">LES RÈGLES</a>
		·
		<a href="/greffe">LES DOSSIERS</a>
		·
		<a href="/regles#ia">À PROPOS</a>
	</p>
</header>

<section class="accueil__hero">
	<p class="accueil__eyebrow">LE TRIBUNAL DES PETITS TRACAS</p>
	<h1 class="accueil__title">WAHALA<br />COURT</h1>
	<p class="accueil__pitch">
		Dépose le wahala d’un pote, choisis un rôle — Gemma joue les autres. Le peuple vote, le tribunal tranche.
	</p>

	<figure class="accueil__art">
		<img src="/perso/courtroom-row.svg" alt="Public du tribunal" />
	</figure>

	<div class="accueil__ctas">
		<button class="btn btn--hero" type="button" onclick={() => goto('/depot')}>DÉPOSER UN POTE</button>
		<button class="btn" type="button" onclick={enter}>ENTRER AU TRIBUNAL</button>
	</div>
	<p class="accueil__note">GRATUIT · GEMMA · TOGOLM · PAS UN VRAI TRIBUNAL</p>
</section>

<Steps />
