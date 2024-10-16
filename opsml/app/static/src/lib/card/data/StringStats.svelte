<script lang="ts">
  import type { StringStats } from "$lib/scripts/data/types";
  import {createCategoricalWordVizData, createWordViz} from "$lib/scripts/data/utils";
  import WordViz from "$lib/card/data/WordViz.svelte";
  import { onMount } from "svelte";
  import type { ChartjsData } from "$lib/scripts/types";

  export let stringStats: StringStats;
  export let timestamp: string;
  export let name: string;

  let vizData: ChartjsData;
  $: vizData = vizData;

  export function createDateFromTimestamp(timestamp: string): string {
      const date = new Date(timestamp);
      return date.toDateString();
  }

  onMount(() => {
      let data  = createCategoricalWordVizData(stringStats.word_stats);
      vizData = createWordViz(data.x, data.y);
  });

</script>
<div class="overflow-x-auto">
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

  <div>
      <!-- Additional content for the fourth column -->
  </div>
  </div>
</div>