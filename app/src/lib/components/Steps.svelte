<script lang="ts">
	const steps = [
		{
			num: '01',
			title: 'CHOISISSEZ UN RÔLE',
			desc: 'Juge, procureur, défense ou accusé. L’objection n’est que pour les avocats.'
		},
		{
			num: '02',
			title: 'LISEZ LE DOSSIER',
			desc: 'Charge, pièce, contexte. Optionnel : collez des messages WhatsApp pour l’ADN du pote.'
		},
		{
			num: '03',
			title: 'PLAIDEZ EN AUDIENCE',
			desc: 'Échanges live. Objection ! si vous êtes procureur ou défense. Puis le peuple vote.'
		},
		{
			num: '04',
			title: 'VERDICT PARTAGEABLE',
			desc: 'Peuple vs tribunal Gemma. Rédigez le post et archivez au greffe.'
		}
	] as const;
</script>

<section class="how" aria-labelledby="how-title">
	<p class="how__eyebrow" id="how-title">COMMENT ÇA MARCHE</p>
	<div class="how__cols">
		{#each steps as step}
			<article class="how__col">
				<p class="how__num">{step.num}</p>
				<h3 class="how__title">{step.title}</h3>
				<p class="how__desc">{step.desc}</p>
			</article>
		{/each}
	</div>
	<p class="how__more"><a href="/regles">Règles · conditions · IA →</a></p>
</section>
