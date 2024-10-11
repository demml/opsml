<script lang="ts">

  import { type SpcFeatureDriftProfile } from "$lib/scripts/types";
  import  {type MonitoringVizData} from "$lib/scripts/monitoring/types";
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';
  import SpcStats from "$lib/card/monitoring/SPCStats.svelte";

  export let targetFeature:SpcFeatureDriftProfile;
  export let monitorVizData: MonitoringVizData;

  let driftVizId: string;
  $: driftVizId = "Drift values for " + targetFeature.id;


</script>

<!-- Drift Viz -->
{#if monitorVizData.driftVizData}
  <div class="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-y-1 lg:gap-x-2">
    <div class="col-span-2 xl:col-span-3">
      <SpcTimeChartDiv
        data={monitorVizData.driftVizData.data}
        id={driftVizId}
        options={monitorVizData.driftVizData.options}
        minHeight="min-h-[400px]"
        maxHeight="max-h-[400px]"
      />
      
    </div>
    <div class="col-span-1">
      <SpcStats
        feature_profile={targetFeature}
        featureDistVizData={monitorVizData.featureDistVizData}
      />
    </div>
  </div>
{:else}
  <div class="flex justify-center items-center h-4/5">
    <p class="text-gray-400">No feature values found for the current time period</p>
  </div>
{/if}

        

        