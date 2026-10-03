<script lang="ts">
	import { goto } from '$app/navigation';
	import { VERDICT_LABEL, CATEGORY_LABEL, type ArchiveEntry } from '$lib/data/model';
	import { CASES } from '$lib/data/cases';
	import { session } from '$lib/stores/session.svelte';

	function replay(entry: ArchiveEntry) {
		session.replay(entry);
		goto('/verdict');
	}

	function openCase(index: number) {
		session.selectCase(index);
		goto('/dossier');
	}
</script>

<section class="vault vault--archives">
	<header class="vault__head">
		<p class="vault__path">greffe / archives</p>
		<h1 class="vault__title">Vault · dossiers</h1>
		<p class="vault__lead">
			Résumés soft des affaires — jugées d’abord, puis le catalogue du greffe.
		</p>
	</header>

	{#if session.greffe.length > 0}
		<section class="vault__judged">
			<p class="vault__side-label">[[jugées]]</p>
			<div class="vault__cards">
				{#each session.greffe as entry (entry.caseFile.number)}
					<button type="button" class="vault__card" onclick={() => replay(entry)}>
						<span class="vault__card-kicker">{entry.caseFile.number}</span>
						<span class="vault__card-title">{entry.caseFile.charge}</span>
						<span class="vault__card-props">
							outcome:: {VERDICT_LABEL[entry.verdict.outcome]} · peuple {entry.peopleShare}%
						</span>
						<span class="vault__card-excerpt">« {entry.verdict.sentence} »</span>
					</button>
				{/each}
			</div>
			<p class="vault__hint"><a href="/redaction">Ouvrir la rédaction auto →</a></p>
		</section>
	{/if}

	<section class="vault__catalog">
		<p class="vault__side-label">[[catalogue]] · {CASES.length}</p>
		<div class="vault__files">
			{#each CASES as c, i}
				<button type="button" class="vault__file vault__file--wide" onclick={() => openCase(i)}>
					<span class="vault__file-icon" aria-hidden="true">{String(i + 1).padStart(2, '0')}</span>
					<span class="vault__file-body">
						<span class="vault__file-name">{c.number} · {CATEGORY_LABEL[c.category]}</span>
						<span class="vault__file-preview">{c.charge}</span>
					</span>
					<span class="vault__file-tag">ouvrir</span>
				</button>
			{/each}
		</div>
	</section>
</section>
