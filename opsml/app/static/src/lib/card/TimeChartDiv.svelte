
<script lang="ts">
  import Fa from 'svelte-fa'
  import { faMagnifyingGlassMinus } from '@fortawesome/free-solid-svg-icons';
  import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import 'chartjs-adapter-date-fns';


  export let data;
  export let options;
  export let id;
  export let maxHeight = "max-h-[450px]";
  export let minHeight: string = "min-h-[250px]";
  export let type = 'line';
  
	let ctx;
	let chartCanvas;
  let chart;

  function resetZoom(id) {
    // reset zoom
    // @ts-ignore
    window[id].resetZoom();
  }

  Chart.register(zoomPlugin);
  Chart.register(annotationPlugin);

	onMount(() => {
    createChart();
    
    return () => {
      if (chart) {
        chart.destroy();
      }
    };

	});

  $: if (chart) {

    //check if chart.type is not undefined
    if (chart.type) {
      // log chart id
      console.log('Updating chart with id: ', id);
      chart.destroy();
      ctx = chartCanvas.getContext('2d');
      chart = new Chart(ctx, {

        // @ts-ignore
        type: type,
        data: data,
        options: options
      });
    }

    chart.data = data;
    chart.type = type;
    chart.options = options;
    chart.update();

    // @ts-ignore
    window[id] = chart;

    }

    function createChart() {
    // log chart id
    console.log('Creating chart with id: ', id);
    ctx = chartCanvas.getContext('2d');
    chart = new Chart(ctx, {
      // @ts-ignore
      type: type,
      data: data,
      options: options
    });

    // @ts-ignore
    window[id] = chart;
  }


</script>

<div class="pt-2 pb-10 rounded-2xl {minHeight} {maxHeight} bg-surface-50 border-2 border-primary-500 shadow-md shadow-primary-500">

  <div class="flex justify-between">

    <div class="text-primary-500 text-lg font-bold pl-4 pt-1 pb-2">{id}</div>

    <div class="flex justify-end">

    <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => resetZoom(id)}>
        <Fa class="h-3" icon={faMagnifyingGlassMinus}/>
        <header class="text-white text-xs">Reset Zoom</header>
    </button>
    </div>
  </div>  
  <canvas bind:this={chartCanvas} id={id}></canvas>
</div>