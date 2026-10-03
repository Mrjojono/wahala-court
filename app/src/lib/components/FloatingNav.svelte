<script lang="ts">
	import { page } from '$app/state';

	const links = [
		{ href: '/', label: 'ACCUEIL' },
		{ href: '/dossier', label: 'DOSSIER' },
		{ href: '/debat', label: 'AUDIENCE' },
		{ href: '/redaction', label: 'RÉDACTION' },
		{ href: '/greffe', label: 'ARCHIVES' }
	] as const;

	const path = $derived(page.url.pathname);
</script>

<nav class="floating-nav" aria-label="Navigation Wahala Court">
	<a class="floating-nav__brand" href="/">
		<span class="floating-nav__mark" aria-hidden="true">W</span>
		<span class="floating-nav__word">
			<span>WAHALA</span>
			<span class="floating-nav__court">COURT</span>
		</span>
	</a>

	<div class="floating-nav__divider" aria-hidden="true"></div>

	<div class="floating-nav__links">
		{#each links as link}
			<a
				class="floating-nav__link"
				class:is-active={path === link.href || (link.href !== '/' && path.startsWith(link.href))}
				href={link.href}
			>
				{link.label}
			</a>
		{/each}
	</div>

	<a class="floating-nav__cta" href="/depot">DÉPOSER</a>
</nav>
