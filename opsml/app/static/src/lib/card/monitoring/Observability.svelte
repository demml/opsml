<script lang="ts">
  import type { RouteVizData } from '$lib/scripts/monitoring/utils';
    import { Accordion, AccordionItem } from '@skeletonlabs/skeleton';
    import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';

    export let routeViz: RouteVizData[];
</script>

{#each routeViz as route}
<SpcTimeChartDiv
                                      data={route.requestViz.data}
                                      id="Requests/sec"
                                      options={route.requestViz.options}
                                      minHeight="min-h-[300px]"
                                      maxHeight="max-h-[300px]"
                                    />
{/each}
<div class="flex flex-col pt-2 pb-16">
    <div class="text-primary-500 text-2xl font-bold pt-2 pb-1">Observability</div>
    <div class="border border-2 border-primary-500 w-full mb-2"></div>
    <Accordion>
        {#each routeViz as route}

            <AccordionItem class="bg-surface-50 rounded-lg border border-2 border-primary-500">
                <svelte:fragment slot="summary"><p class="text-primary-500 text-lg font-bold">{route.route_name}</p></svelte:fragment>
                <svelte:fragment slot="content">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <!-- First Parent Column -->
                        <div class="lg:col-span-1">
                            <div class="grid grid-cols-2 gap-4">
                                <div class="card bg-white p-4 rounded-lg shadow">
                                  <h3 class="text-lg font-bold text-center text-secondary-500">Requests/s</h3>
                                    <p class="text-lg text-center">{route.requests_per_sec.toFixed(2)}</p>
                                </div>
                                <div class="card bg-white p-4 rounded-lg shadow">
                                  <h3 class="text-lg font-bold text-center text-scouter_red">Errors</h3>
                                    <p class="text-lg text-center">{route.errors}</p>
                                </div>
                            </div>
                        </div>
                        <!-- Second Parent Column -->
                        <div class="lg:col-span-2">
                            <div class="grid grid-cols-2 gap-4">
                                <div class="card bg-white p-4 rounded-lg shadow">
                                    <SpcTimeChartDiv
                                      data={route.requestViz.data}
                                      id="Requests/sec"
                                      options={route.requestViz.options}
                                      minHeight="min-h-[300px]"
                                      maxHeight="max-h-[300px]"
                                    />
                                </div>
                                <div class="card bg-white p-4 rounded-lg shadow">
                                    <h3 class="text-lg font-bold">Placeholder</h3>
                                    <p>Placeholder</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </svelte:fragment>
            </AccordionItem>
            
        {/each}
        <!-- ... -->
    </Accordion>
</div>