<script lang="ts">
  import type { RouteVizData } from '$lib/scripts/monitoring/utils';
    import { Accordion, AccordionItem } from '@skeletonlabs/skeleton';

    export let routeViz: RouteVizData[];
</script>


<div class="flex flex-col pt-2 pb-16">
    <div class="text-primary-500 text-2xl font-bold pt-2 pb-1">Observability</div>
    <div class="border border-2 border-primary-500 w-full mb-2"></div>
    <Accordion>
        {#each routeViz as route}

            <AccordionItem class="bg-surface-50 rounded-lg border border-2 border-primary-500">
                <svelte:fragment slot="summary"><p class="text-primary-500 text-lg font-bold">{route.route_name}</p></svelte:fragment>
                <svelte:fragment slot="content">(content)</svelte:fragment>
            </AccordionItem>
            
        {/each}
        <!-- ... -->
    </Accordion>
</div>