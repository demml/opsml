<script lang="ts">
  import { type RouteVizData, getObservabilityMetrics, createObservabilityViz } from '$lib/scripts/monitoring/utils';
  import { Accordion, AccordionItem } from '@skeletonlabs/skeleton';
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';

  export let routeViz: RouteVizData[];
  export let repository: string;
  export let name: string;
  export let version: string;
  export let timeWindow: string;
  export let max_data_points: number;


  async function refresh() {
    const observabilityMetrics = await getObservabilityMetrics(
      repository!,
      name!,
      version!,
      timeWindow,
      max_data_points
    );

    routeViz = [];
    if (observabilityMetrics.metrics.length > 0) {
      routeViz = createObservabilityViz(observabilityMetrics);
    }
  }

  $: timeWindow, refresh();



</script>

{#if routeViz.length > 0}

  <div class="flex flex-col pt-2 pb-16">
      <div class="text-primary-500 text-2xl font-bold pt-2 pb-1">Observability</div>
      <div class="border border-2 border-primary-500 w-full mb-2"></div>
      <Accordion>
          {#each routeViz as route}

            <AccordionItem class="bg-surface-50 rounded-lg border border-2 border-primary-500">
              <svelte:fragment slot="summary"><p class="text-primary-500 text-lg font-bold">{route.route_name}</p></svelte:fragment>
              <svelte:fragment slot="content">

                <div class="grid grid-cols- lg:grid-cols-7 gap-4">
                  <!-- First Parent Column -->
                  <div class="lg:col-span-1 self-center">
                    <div class="grid grid-cols-1 gap-4">
                      <div class="card p-4 rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md shadow-primary-500">
                        <h3 class="text-lg font-bold text-center text-secondary-500">Requests (thousands)</h3>
                          <p class="text-lg text-center">{route.requests_per_sec/1000}</p>
                      </div>
                      <div class="card p-4 rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md shadow-primary-500">
                        <h3 class="text-lg font-bold text-center text-scouter_red">Errors</h3>
                          <p class="text-lg text-center">{route.errors}</p>
                      </div>
                    </div>
                  </div>
                  <!-- Second Parent Column -->
                  <div class="lg:col-span-6">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <SpcTimeChartDiv
                          data={route.requestViz.data}
                          id="Requests/sec"
                          options={route.requestViz.options}
                          minHeight="min-h-[300px]"
                          maxHeight="max-h-[300px]"
                        />
                      <SpcTimeChartDiv
                        data={route.latencyViz.data}
                        id="Latency (ms)"
                        options={route.latencyViz.options}
                        minHeight="min-h-[300px]"
                        maxHeight="max-h-[300px]"
                      />
                    </div>
                  </div>
                </div>
              </svelte:fragment>
            </AccordionItem>
              
          {/each}
          <!-- ... -->
      </Accordion>
  </div>
    
{/if}