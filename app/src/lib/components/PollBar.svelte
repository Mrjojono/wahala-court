<script lang="ts">
	interface Props {
		guilty: number;
		innocent: number;
		jurors?: number;
	}

	let { guilty, innocent, jurors = 1842 }: Props = $props();
</script>

<div class="poll-bar" aria-label="Tendance du jury">
	<div class="poll-bar__meta">
		<span>{guilty}% TENDANCE CONDAMNATION</span>
		<span>{jurors.toLocaleString('fr-FR')} JURÉS ENREGISTRÉS</span>
		<span>{innocent}% ACQUITTEMENT</span>
	</div>
	<div class="poll-bar__track" role="presentation">
		<div class="poll-bar__guilty" style:width="{guilty}%"></div>
		<div class="poll-bar__innocent" style:width="{innocent}%"></div>
	</div>
</div>
