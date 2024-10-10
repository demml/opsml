
<script lang="ts">
    import { type ChartjsData, type SpcDriftProfile, type SpcFeatureDriftProfile, type FeatureDriftValues, TimeWindow, type MonitorAlerts , ProfileType } from "$lib/scripts/types";
    import  {type MonitoringVizData} from "$lib/scripts/monitoring/types";
    import { rebuildSpcDriftViz } from "$lib/scripts/monitoring/utils";
    import logo from '$lib/images/opsml-green.ico';
    import { onMount } from 'svelte';
    import scouter_logo from '$lib/images/scouter.svg';
    import Dropdown from "$lib/components/Dropdown.svelte";
    import SPCProfile from "$lib/card/monitoring/SPCProfile.svelte";
    import Test from "$lib/card/monitoring/Test.svelte";
    import { goto } from '$app/navigation';


    /** @type {import('./$types').PageData} */
    export let data;


    let driftProfiles: Map<ProfileType, SpcDriftProfile>;
    $: driftProfiles = data.driftProfiles;

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

    let alerts: MonitorAlerts;
    $: alerts = data.alerts;

    let profileType: ProfileType;
    $: profileType = data.type;

    let timeWindow: string;
    $: timeWindow = data.timeWindow;


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


<Test
    {driftProfiles}
    {targetFeature}
    {monitorVizData}
    {alerts}
    {profileType}
    {timeWindow}
    {max_data_points}
    {name}
    {repository}
    {version}
/>



