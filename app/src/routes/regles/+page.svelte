<script lang="ts">
	import { CAN_OBJECT, PERSONA_LABEL } from '$lib/data/model';
</script>

<article class="rules">
	<header class="rules__head">
		<p class="rules__kicker">WAHALA COURT</p>
		<h1 class="rules__title">RÈGLES & CONDITIONS</h1>
		<p class="rules__lead">
			Petit procès tabloïd des wahalas du quotidien. Pas un vrai tribunal. Pas un conseil juridique.
		</p>
	</header>

	<section class="rules__block">
		<h2>Parcours</h2>
		<ol>
			<li><strong>Rôle</strong> — choisissez juge, procureur, défense ou accusé.</li>
			<li><strong>Dossier</strong> — lisez la charge ; optionnel : ADN WhatsApp du pote.</li>
			<li><strong>Audience</strong> — plaidez (min. 2 échanges). Objection pour les avocats.</li>
			<li><strong>Vote</strong> — le peuple tranche, puis la chambre Gemma délibère.</li>
			<li><strong>Verdict</strong> — contraste peuple vs tribunal, partage, rédaction, greffe.</li>
		</ol>
	</section>

	<section class="rules__block">
		<h2>Qui fait quoi</h2>
		<ul>
			<li><strong>{PERSONA_LABEL.juge}</strong> — préside, tranche les objections, ne lève pas d’objection.</li>
			<li>
				<strong>{PERSONA_LABEL.procureur}</strong> /
				<strong>{PERSONA_LABEL.defense}</strong> — plaident et peuvent lever
				<strong>OBJECTION !</strong>
				({CAN_OBJECT.length} rôles · max 3 / audience · cooldown).
			</li>
			<li><strong>{PERSONA_LABEL.accuse}</strong> — se défend à la barre, pas d’objection formelle.</li>
			<li><strong>Greffier</strong> — annonces scriptées (pas d’IA).</li>
		</ul>
	</section>

	<section class="rules__block">
		<h2>Objection</h2>
		<p>
			Effet front : tampon + réplique, puis le juge tranche (retenue / rejetée). Pas un vrai incident
			juridique — c’est du spectacle wahala.
		</p>
	</section>

	<section class="rules__block">
		<h2>IA & données</h2>
		<ul>
			<li>
				<strong>Génération</strong> — Gemma via Ollama en local (open-weight). Si Ollama est off, fallback
				scripté.
			</li>
			<li>
				<strong>RAG</strong> — recherche TogoLM (corpus togolais open source) pour nourrir les citations.
				Pas de génération Gemini côté TogoLM dans ce projet.
			</li>
			<li>
				<strong>Vie privée</strong> — les messages WhatsApp collés pour l’ADN restent dans votre session
				navigateur + éventuellement votre Ollama local. Ne collez rien de sensible.
			</li>
			<li>
				<strong>Fiction</strong> — sentences et « articles » sont comiques. Ce n’est pas du droit positif.
			</li>
		</ul>
	</section>

	<section class="rules__block">
		<h2>Conditions d’usage (lite)</h2>
		<ul>
			<li>Usage perso / démo / hackathon — pas d’usage commercial sans licence claire des assets.</li>
			<li>Interdit : harcèlement, doxxing, contenus illégaux via les prompts.</li>
			<li>Vous gardez la responsabilité de ce que vous partagez (posts, captures).</li>
			<li>Sources open : crédit TogoLM / Gemma / design Wahala Court dans vos posts DEV.</li>
		</ul>
	</section>

	<p class="rules__back"><a href="/">← Retour à l’accueil</a> · <a href="/role">Entrer au tribunal →</a></p>
</article>
