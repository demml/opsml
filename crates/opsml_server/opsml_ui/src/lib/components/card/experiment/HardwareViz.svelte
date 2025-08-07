<script lang="ts">
    import TimeSeries from '$lib/components/viz/TimeSeries.svelte';


    let { 
        xValues,
        yValues,
        vizLabel,
        yLabel,
     } = $props<{
        xValues: string[],
        yValues: number[],
        vizLabel: string,
        yLabel: string,
     }>();
  
    let resetZoom: boolean = $state(false);
  
    let resetZoomClicked = () => {
      resetZoom = !resetZoom;
    }
  
  </script>
  

<div class="flex flex-col">
  <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full">
    <div class="items-center mr-2 font-bold text-primary-800">{vizLabel}</div>
    <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
      <div class="text-black">Reset Zoom</div>
    </button>
  </div>

  <TimeSeries
    baselineValue={undefined}
    timestamps={xValues}
    values={yValues}
    label={vizLabel}
    yLabel={yLabel}
    bind:resetZoom={resetZoom}
  />

</div> 
