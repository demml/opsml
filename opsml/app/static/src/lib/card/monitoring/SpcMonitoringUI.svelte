<script lang="ts">

  import { type SpcFeatureDriftProfile } from "$lib/scripts/types";
  import  {type MonitoringVizData, type MonitorData} from "$lib/scripts/monitoring/types";
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';
  import SpcStats from "$lib/card/monitoring/SpcStats.svelte";

  export let monitorData: MonitorData;

  let driftVizId: string;
  $: driftVizId = "Drift values for " + monitorData.feature.id;

  let feature: SpcFeatureDriftProfile;
  $: feature = monitorData.feature;

  let vizData: MonitoringVizData;
  $: vizData = monitorData.vizData;




</script>


  <div class="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-y-1 lg:gap-x-2">
    <div class="col-span-2 xl:col-span-3">
      <SpcTimeChartDiv
        data={vizData.driftVizData.data}
        id={driftVizId}
        options={vizData.driftVizData.options}
        minHeight="min-h-[400px]"
        maxHeight="max-h-[400px]"
      />
      
    </div>
    <div class="col-span-1">
      <SpcStats
        feature_profile={feature}
        featureDistVizData={vizData.featureDistVizData}
      />
    </div>
  </div>


        

        