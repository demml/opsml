
<script lang="ts">
    import { type SpcFeatureDriftProfile, type MonitorAlerts , ProfileType, type ChartjsData } from "$lib/scripts/types";
    import  {type MonitoringVizData} from "$lib/scripts/monitoring/types";
    import { rebuildSpcDriftViz , getAlertMetrics, createAlertMetricViz} from "$lib/scripts/monitoring/utils";
    import { onMount } from 'svelte';
    import SpcMonitorUI from "$lib/card/monitoring/SpcMonitoringUI.svelte";
    import SpcAlertUI from "$lib/card/monitoring/SpcAlertUI.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    let targetFeature: SpcFeatureDriftProfile;
    $: targetFeature = data.targetFeature;

    let monitorVizData: MonitoringVizData;
    $: monitorVizData = data.monitorVizData;

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
    alerts = data.alerts;

    let alertMetricVizData: ChartjsData;
    alertMetricVizData = data.alertMetricVizData;


    async function reloadAlerts(maxDataPoints) {
        console.log(maxDataPoints);
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
  
      if (window.innerWidth < 640) { // Check if screen width is less than 768px
        max_data_points = 100;

      } else if (window.innerWidth < 768) { // Check if screen width is greater than or equal to 768px and less than 1024px

        max_data_points = 200;

      } else if (window.innerWidth < 1024) {
        max_data_points = 400;
      
      } else if (window.innerWidth < 1280) {
        max_data_points = 600;
        
      } else if (window.innerWidth < 1536) {
        max_data_points = 800;

      } else { // Check if screen width is greater than or equal to 1024px
        // Call your function for large screen size
        max_data_points = 1000;
      }
      
      //await navigate();
      monitorVizData = await rebuildSpcDriftViz(repository, name, version, timeWindow, max_data_points, targetFeature.id, targetFeature);
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


<SpcMonitorUI {targetFeature} {monitorVizData} />
<SpcAlertUI {alerts} {alertMetricVizData} />



