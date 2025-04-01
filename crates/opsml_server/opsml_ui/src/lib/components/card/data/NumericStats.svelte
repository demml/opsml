<script lang="ts">
  import type { NumericStats } from "./types";


let { 
  numericData
} = $props<{
  numericData: NumericStats;
}>();


</script>

<div class="grid grid-cols-5 gap-x-2 min-w-max h-auto pt-2">
  <div class="col-span-1">
    <div class="flex flex-row justify-between items-center p-2">

      <!-- General stats -->
      <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50">
        <div class="flex items-center justify-center bg-primary-100 border-b-2 border-primary-950 rounded-t-lg">
          <div class="font-bold text-primary-950">General Stats</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Distinct:</div>
          <div class="text-black">{numericData.distinct.count} ({numericData.distinct.percent}%)</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Mean:</div>
          <div class="text-black">{numericData.stddev.toFixed(3)}</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Minimum:</div>
          <div class="text-black">{numericData.min.toFixed(3)}</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Maximum:</div>
          <div class="text-black">{numericData.min.toFixed(3)}</div>
        </div>
      </div>

      <!-- Quantiles -->
      <div class="flex flex-col gap-1 border-2 border-black rounded-lg bg-surface-50">
        <div class="flex items-center justify-center bg-primary-100 border-b-2 border-primary-950 rounded-t-lg">
          <div class="font-bold text-primary-950">Quantiles</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Q25:</div>
          <div class="text-black">{numericData.quantiles.q25.toFixed(3)}</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Q50:</div>
          <div class="text-black">{numericData.quantiles.q50.toFixed(3)}</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Q75:</div>
          <div class="text-black">{numericData.quantiles.q75.toFixed(3)}</div>
        </div>
        <div class="flex flex-row items-center px-2">
          <div class="font-bold text-primary-800 pr-1">Q99:</div>
          <div class="text-black">{numericData.quantiles.q99.toFixed(3)}</div>
        </div>
      </div>
    </div>


  </div>
</div>