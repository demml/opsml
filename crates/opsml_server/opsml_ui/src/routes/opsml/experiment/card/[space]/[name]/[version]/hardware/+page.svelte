<script lang="ts">
  import type { UiHardwareMetrics } from '$lib/components/card/experiment/types';
  import type { PageProps } from './$types';
  let { data }: PageProps = $props();
  import HardwareViz from '$lib/components/card/experiment/HardwareViz.svelte';

  let metrics: UiHardwareMetrics = data.hardwareMetrics;

  let resetZoom: boolean = $state(false);

  let resetZoomClicked = () => {
    resetZoom = !resetZoom;
  }

</script>

<div class="flex-1 mx-auto w-10/12 pb-10 flex justify-center overflow-auto px-4">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full pt-4">

    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      <HardwareViz
        xValues={metrics.createdAt}
        yValues={metrics.cpuUtilization}
        vizLabel="CPU Utilization"
        yLabel="Utilization (%)"
      />
    </div>

    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      <HardwareViz
        xValues={metrics.createdAt}
        yValues={metrics.usedPercentMemory}
        vizLabel="Memory Utilization"
        yLabel="Utilization (%)"
      />
    </div>

    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      <HardwareViz
        xValues={metrics.createdAt}
        yValues={metrics.networkMbRecv}
        vizLabel="Network Received"
        yLabel="Received (MB)"
      />
    </div>


    <div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
      <HardwareViz
        xValues={metrics.createdAt}
        yValues={metrics.networkMbSent}
        vizLabel="Network Sent"
        yLabel="Sent (MB)"
      />
    </div>

  </div>
</div>




