<script lang="ts">
	interface Props {
		label: string;
		tone?: 'red' | 'gold' | 'ink' | 'green';
		tilt?: boolean;
		class?: string;
	}

	let { label, tone = 'red', tilt = false, class: klass = '' }: Props = $props();
</script>

<span class={['stamp', `stamp--${tone}`, tilt && 'stamp--tilt', klass]}>{label}</span>
