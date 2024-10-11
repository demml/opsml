
<script lang="ts">
    import { type MonitorAlerts , ProfileType, type ChartjsData } from "$lib/scripts/types";
    import  {type MonitorData } from "$lib/scripts/monitoring/types";
    import { getScreenSize } from "$lib/scripts/utils";
    import { rebuildSpcDriftViz , getAlertMetrics, createAlertMetricViz} from "$lib/scripts/monitoring/utils";
    import { onMount } from 'svelte';
    import SpcMonitorUI from "$lib/card/monitoring/SpcMonitoringUI.svelte";
    import SpcAlertUI from "$lib/card/monitoring/SpcAlertUI.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    let monitorData: MonitorData;
    $: monitorData = data.monitorData;

    let max_data_points: number;
    $: max_data_points = data.max_data_points;

    let name: string;
    $: name = data.name;

    let repository: string;
    $: repository = data.repository;

    let version: string;
    $: version = data.version;

    let profileType: ProfileType;
    $: profileType = data.type;

    let timeWindow: string;
    $: timeWindow = data.timeWindow;

    let alerts: MonitorAlerts;
    $: alerts = data.alerts;

    let alertMetricVizData: ChartjsData;
    $: alertMetricVizData = data.alertMetricVizData;


    async function reloadAlerts(maxDataPoints) {
      let alertMetrics = await getAlertMetrics(
        repository,
        name,
        version,
        timeWindow,
        maxDataPoints
      );

      let alertMetricViz = await createAlertMetricViz(alertMetrics);
      alertMetricVizData = alertMetricViz;
    }

    async function checkScreenSize() {
      max_data_points = getScreenSize();
     let  monitorVizData = await rebuildSpcDriftViz(repository, name, version, timeWindow, max_data_points, monitorData.feature.id, monitorData.feature);

      monitorData = {
        vizData: monitorVizData,
        feature: monitorData.feature,
      };
      await reloadAlerts(max_data_points);

    }

    function debounce(func, time) {
      var time = time || 100; // 100 by default if no param
      var timer;
      return function(event){
          if(timer) clearTimeout(timer);
          timer = setTimeout(func, time, event);
      };
    }


    onMount (() => {
      window.addEventListener('resize', debounce(checkScreenSize, 400)); 
    });


    function resetZoom(id) {
      // reset zoom
      // @ts-ignore
      window[id].resetZoom();
    }



</script>


<SpcMonitorUI {monitorData} />
<SpcAlertUI 
          {alerts} 
          {alertMetricVizData} 
          {repository} 
          {name} 
          {version} 
          {timeWindow}
        />



