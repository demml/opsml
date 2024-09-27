<script lang="ts">

    import { type ChartjsData, type DriftProfile, type FeatureDriftProfile,  type MonitorAlerts , ProfileType } from "$lib/scripts/types";
    import { rebuildDriftViz } from "$lib/scripts/monitoring/utils";
    import TimeChartDiv from '$lib/card/TimeChartDiv.svelte';
    import AlertDiv from "$lib/card/monitoring/Alerts.svelte";
    import SpcStats from "$lib/card/monitoring/SPCStats.svelte";
    import Fa from 'svelte-fa';
    import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
  

    export let driftProfiles: Map<ProfileType, DriftProfile>;
    export let targetFeature:FeatureDriftProfile;
    export let driftVizData: ChartjsData;
    export let featureDistVizData: ChartjsData;
    export let alertMetricVizData: ChartjsData;
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
      let rebuiltViz = await rebuildDriftViz(repository, name, version, timeWindow, max_data_points, feature, targetFeature);
  
      driftVizData = rebuiltViz[0];
      featureDistVizData = rebuiltViz[1];
  
    }
    
    function handleFeatureUpdate(event) {
    
      updateFeatureValues(event.detail.feature);
    }
  
  </script>

          <!-- Drift Viz -->
          {#if driftVizData}
            <div class="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-y-1 lg:gap-x-2">
              <div class="col-span-2 xl:col-span-3">
                <TimeChartDiv
                  data={driftVizData.data}
                  id={driftVizId}
                  options={driftVizData.options}
                  minHeight="min-h-[300px] lg:min-h-[400px]"
                  maxHeight="max-h-[300px] lg:min-h-[400px]"
                />
              </div>
              <div class="col-span-1">
                <SpcStats
                  feature_profile={targetFeature}
                  featureDistVizData={featureDistVizData}
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
                {#if alertMetricVizData}
                  <TimeChartDiv
                    data={alertMetricVizData.data}
                    id={alertMeticsId}
                    options={alertMetricVizData.options}
                    minHeight="min-h-[300px]"
                    maxHeight="max-h-[300px]"
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
                <div id="table" class="col-span-1 min-h-[250px] max-h-[450px] rounded-2xl border border-2 border-primary-500 overflow-y-auto mb-4 shadow-md">
                  <AlertDiv alerts={alerts} on:switchFeature={handleFeatureUpdate}/>
                </div>
              </div>
            </div>
          </div>
