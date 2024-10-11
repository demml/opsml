<script lang="ts">

  import { type SpcFeatureDriftProfile } from "$lib/scripts/types";
  import  {type MonitoringVizData, type MonitorData} from "$lib/scripts/monitoring/types";
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';
  import SpcStats from "$lib/card/monitoring/SPCStats.svelte";


  export let monitorData: MonitorData;

  let driftVizId: string;
  $: driftVizId = "Drift values for " + monitorData.feature.id;


</script>


  <div class="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-y-1 lg:gap-x-2">
    <div class="col-span-2 xl:col-span-3">
      <SpcTimeChartDiv
        data={monitorData.vizData.driftVizData.data}
        id={driftVizId}
        options={monitorData.vizData.driftVizData.options}
        minHeight="min-h-[400px]"
        maxHeight="max-h-[400px]"
      />
      
    </div>
    <div class="col-span-1">
      <SpcStats
        feature_profile={monitorData.feature}
        featureDistVizData={monitorData.vizData.featureDistVizData}
        id={monitorData.feature.id}
      />
    </div>
  </div>


        

        