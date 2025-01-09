<script lang="ts">
  import type { StringStats } from "$lib/scripts/data/types";
  import {createCategoricalWordVizData, createBarViz} from "$lib/scripts/data/utils";
  import WordViz from "$lib/card/data/WordViz.svelte";
  import CorrelationViz from "./CorrelationViz.svelte";
  import { onMount } from "svelte";
  import type { ChartjsData } from "$lib/scripts/types";

  export let stringStats: StringStats;
  export let correlations: Record<string, number> | undefined;
  export let timestamp: string;
  export let name: string;


  let vizData: ChartjsData;
  let correlationVizData: ChartjsData;
  let x_sorted: string[] = [];
  let y_sorted: number[] = [];

  export function createDateFromTimestamp(timestamp: string): string {
      const date = new Date(timestamp);
      return date.toDateString();
  }

  onMount(() => {
      let data  = createCategoricalWordVizData(stringStats.word_stats);
      vizData = createBarViz(data.x, data.y, "Words");

      if (correlations) {
        // sort the correlations by value
        const sorted = Object.entries(correlations).sort((a, b) => b[1] - a[1]);

        // get keys and values
        x_sorted = sorted.map((entry) => entry[0]);
        y_sorted = sorted.map((entry) => entry[1]);

        correlationVizData = createBarViz(x_sorted, y_sorted, "Feature");
      }
  });

</script>
<div class="overflow-x-auto overflow-y-auto">

  <div class="grid grid-cols-5 gap-x-2 min-w-max">
      <div class="content-center">
        <div class="px-2 text-darkpurple font-bold">Overview</div>
        <div class="flex flex-col">
          <div class="inline-flex items-center overflow-hidden w-fit">
            <div class="px-2 text-sm font-semibold">Name</div>
            <div class="flex text-sm px-1.5 text-gray-800">
                {name}
            </div>
          </div>
          <div class="inline-flex items-center overflow-hidden w-fit">
              <div class="px-2 text-sm font-semibold">Distinct</div>
              <div class="flex text-sm px-1.5 text-gray-800">
                  {stringStats.distinct.count} ({stringStats.distinct.percent}%)
              </div>
          </div>
          <div class="inline-flex items-center overflow-hidden w-fit">
              <div class="px-2 text-sm font-semibold">Created At</div>
              <div class="flex text-sm px-1.5 text-gray-800">
                  {createDateFromTimestamp(timestamp)}
              </div>
          </div>
        </div>
      </div>

      <div class="border-l border-gray-300 content-center">
        <div class="px-2 text-darkpurple font-bold">Character Statistics</div>
        <div class="flex flex-col">
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Min Length</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {stringStats.char_stats.min_length}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Max Length</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {stringStats.char_stats.max_length}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Median Length</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {stringStats.char_stats.median_length}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Mean Length</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {stringStats.char_stats.mean_length}
                </div>
            </div>
        </div>
      </div>


    <div class="col-span-3 content-center border-l border-gray-300">
      <div class="pl-1">
        {#if vizData}
          <WordViz 
          data={vizData.data}
          options={vizData.options}
          />
        {/if}
      </div>
    </div>
  </div>

  {#if correlations}
  <div class="grid grid-cols-5 gap-x-2 min-w-max mt-4">
    <div class="content-center colspan-1">
      <div class="px-2 text-darkpurple font-bold">Correlations</div>

      <div class="max-h-48 overflow-y-auto">
        <table class="table-compact table-cell-fit table-hover text-xs text-center min-w-full">
          <thead class="bg-primary-200 sticky top-0">
            <tr>
              <th class="text-sm text-center py-2">Feature</th>
              <th class="text-sm text-center py-2">Value</th>

           
              
            </tr>
          </thead>
          <tbody>
            {#each x_sorted as feature, i}
              <tr class="even:bg-gray-100">
                <td class="text-xs">{feature}</td>
    
                {#if Math.abs(y_sorted[i]) >= 0.2}
                  <td class="text-xs"><span class="badge variant-soft-error">{y_sorted[i]}</span></td>
                {:else}
                  <td class="text-xs">{y_sorted[i].toFixed(2)}</td>
                {/if}

              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-span-4 content-center border-l border-gray-300">
      <div class="pl-1 max-w-full">
        {#if correlationVizData}
          <CorrelationViz
          data={correlationVizData.data}
          options={correlationVizData.options}
          />
        {/if}
      </div>
    </div>
  </div>
  {/if}
</div>