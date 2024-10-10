<script lang="ts">

  import { type ChartjsData, type SpcDriftProfile, type SpcFeatureDriftProfile,  type MonitorAlerts , ProfileType } from "$lib/scripts/types";
  import  {type MonitoringVizData} from "$lib/scripts/monitoring/types";
  import { rebuildSpcDriftViz } from "$lib/scripts/monitoring/utils";
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';
  import AlertDiv from "$lib/card/monitoring/Alerts.svelte";
  import SpcStats from "$lib/card/monitoring/SPCStats.svelte";
  import Fa from 'svelte-fa';
  import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
  import TimeChartDiv from '$lib/card/TimeChartDiv.svelte';

  export let driftProfiles: Map<ProfileType, SpcDriftProfile>;
  export let targetFeature:SpcFeatureDriftProfile;
  export let monitorVizData: MonitoringVizData;
  export let timeWindow: string;
  export let max_data_points: number;
  export let name: string;
  export let repository: string;;
  export let version: string;
  export let alerts: MonitorAlerts;
  export let profileType: ProfileType;

  let driftVizId: string;
  $: driftVizId = "Drift values for " + targetFeature.id;

  let alertMeticsId: string;
  $: alertMeticsId = 'Alert Metrics';


 async function updateFeatureValues(feature:string) {

   if (feature === targetFeature.id) {
     return;
   }
   targetFeature = driftProfiles[profileType].features[feature];
   monitorVizData = await rebuildSpcDriftViz(repository, name, version, timeWindow, max_data_points, feature, targetFeature);
 }
 
 function handleFeatureUpdate(event) {
 
   updateFeatureValues(event.detail.feature);
 }

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

        <div class="flex flex-col pt-2">
          <div class="text-primary-500 text-2xl font-bold pt-2 pb-1">Alerts</div>
          <div class="border border-2 border-primary-500 w-full mb-2"></div>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-1">
            <div class="lg:mr-2 lg:col-span-2">
              <div class="flex flex-row items-center">
                <Fa icon={faTriangleExclamation} size="lg" color="#f54d55"/>
                <header class="pl-2 text-secondary-600 text-lg font-bold">Alert History</header>
              </div>
              {#if monitorVizData.alertMetricVizData}
                <TimeChartDiv
                  data={monitorVizData.alertMetricVizData.data}
                  id={alertMeticsId}
                  options={monitorVizData.alertMetricVizData.options}
                  minHeight="min-h-[300px]"
                  maxHeight="max-h-[300px]"
                  type="bar"
                />
              {:else}
                <div class="flex justify-center items-center h-4/5">
                  <p class="text-gray-400">No feature values found for the current time period</p>
                </div>
              {/if}
            </div>
            <div>
              <div class="flex flex-row items-center">
                <Fa icon={faTriangleExclamation} size="lg" color="#f54d55"/>
                <header class="pl-2 text-secondary-600 text-lg font-bold">Active Alerts</header>
              </div>
              <div id="table" class="col-span-1 min-h-[300px] max-h-[300px] rounded-2xl border border-2 border-primary-500 overflow-y-auto mb-4 shadow-md shadow-primary-500">
                <AlertDiv alerts={alerts}/>
              </div>
            </div>
          </div>
        </div>

        