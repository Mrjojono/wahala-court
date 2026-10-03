<script lang="ts">
	import type { PersonaName } from '$lib/data/model';
	import { PERSONA_LABEL, PERSONA_ART } from '$lib/data/model';

	interface Props {
		who: PersonaName;
		size?: 'sm' | 'md' | 'lg' | 'xl' | 'fill';
		figure?: boolean;
		label?: string;
		class?: string;
		src?: string;
	}

	let { who, size = 'md', figure = false, label, class: klass = '', src }: Props = $props();

	const accessibleLabel = $derived(label ?? PERSONA_LABEL[who]);
	const art = $derived(src ?? PERSONA_ART[who]);
	const cls = $derived(
		`persona persona--${who} persona--${size}${figure ? ' persona--figure' : ''} ${klass}`
	);
</script>

<span class={cls} role="img" aria-label={accessibleLabel}>
	<img src={art} alt="" loading="lazy" decoding="async" />
</span>
