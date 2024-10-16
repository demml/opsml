<script lang="ts">
    import type { NumericStats } from "$lib/scripts/data/types";
    import {createHistViz} from "$lib/scripts/data/utils";
    import HistViz from "./HistViz.svelte";
    import { onMount } from "svelte";
    import type { ChartjsData } from "$lib/scripts/types";
  
    export let numericStats: NumericStats;
    export let timestamp: string;
    export let name: string;
  
    let vizData: ChartjsData;
    $: vizData = vizData;
  
    export function createDateFromTimestamp(timestamp: string): string {
        const date = new Date(timestamp);
        return date.toDateString();
    }
  
    onMount(() => {
        vizData  = createHistViz(numericStats.histogram);
        console.log(vizData);
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
                  {numericStats.distinct.count} ({numericStats.distinct.percent}%)
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
        <div class="px-2 text-darkpurple font-bold">Numeric Statistics</div>
        <div class="flex flex-col">
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Mean</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.mean.toFixed(3)}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Standard Dev</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.stddev.toFixed(3)}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Minimum</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.min.toFixed(3)}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Quantile 25</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.quantiles.q25.toFixed(3)}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Quantile 50</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.quantiles.q50.toFixed(3)}
                </div>
            </div>
            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Quantile 75</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.quantiles.q75.toFixed(3)}
                </div>
            </div>

            <div class="inline-flex items-center overflow-hidden w-fit">
                <div class="px-2 text-sm font-semibold">Quantile 99</div>
                <div class="flex text-sm px-1.5 text-gray-800">
                    {numericStats.quantiles.q99.toFixed(3)}
                </div>
            </div>


        </div>
      </div>
  
      <div class="col-span-3 content-center border-l border-gray-300">
        <div class="pl-1">
          {#if vizData}
              <HistViz
              data={vizData.data}
              options={vizData.options}
              />
          {/if}
        </div>
      </div>
    </div>
  </div>