<script lang="ts">

  import {  ProfileType, type MonitorAlerts, type ChartjsData } from "$lib/scripts/types";
  import { getAlertMetrics, createAlertMetricViz } from "$lib/scripts/monitoring/utils";
  import SpcTimeChartDiv from '$lib/card/monitoring/SpcTimeChart.svelte';
  import AlertDiv from "$lib/card/monitoring/Alerts.svelte";
  import Fa from 'svelte-fa';
  import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
  import { goto } from "$app/navigation";

  export let alertMetricVizData: ChartjsData;
  export let alerts: MonitorAlerts;
  export let repository: string;
  export let name: string;
  export let version: string;
  export let timeWindow: string;

  let baseURL: string = `/opsml/model/card/monitoring/feature`;


  function handleSwitchFeature(event) {
    const { feature } = event.detail;
    goto(`${baseURL}?name=${name}&repository=${repository}&version=${version}&feature=${feature}&type=${ProfileType.SPC}&time=${timeWindow}`,  { invalidateAll: false, noScroll: true });


    // Add your logic to handle the feature switch here
  }

</script>

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
          <SpcTimeChartDiv
            data={alertMetricVizData.data}
            id='Alert Metrics'
            options={alertMetricVizData.options}
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
          <AlertDiv alerts={alerts} on:switchFeature={handleSwitchFeature}/>
        </div>
      </div>
    </div>
  </div>