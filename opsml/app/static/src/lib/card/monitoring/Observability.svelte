<script lang="ts">
  import type { RouteVizData } from '$lib/scripts/monitoring/utils';
    import { Accordion, AccordionItem } from '@skeletonlabs/skeleton';

    export let routeViz: RouteVizData[];
</script>

<Accordion>
	<AccordionItem open>
		<svelte:fragment slot="lead">(icon)</svelte:fragment>
		<svelte:fragment slot="summary">(summary)</svelte:fragment>
		<svelte:fragment slot="content">(content)</svelte:fragment>
	</AccordionItem>
	<AccordionItem>
		<svelte:fragment slot="lead">(icon)</svelte:fragment>
		<svelte:fragment slot="summary">(summary)</svelte:fragment>
		<svelte:fragment slot="content">(content)</svelte:fragment>
	</AccordionItem>
	<!-- ... -->
</Accordion>