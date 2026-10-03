<script lang="ts">
	interface Props {
		text: string;
		tone?: 'red' | 'ink';
	}

	let { text, tone = 'red' }: Props = $props();
</script>

<div class="alert-stripe alert-stripe--{tone}" role="status">
	<p>{text}</p>
</div>
