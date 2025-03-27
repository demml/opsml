
<script lang="ts">
  import TimeSeries from '../viz/TimeSeries.svelte';
  import 'chartjs-adapter-date-fns';
  import { DriftType } from '$lib/components/monitoring/types';
  import 'chartjs-adapter-date-fns';
  import type { MetricData, SpcDriftFeature, BinnedPsiMetric, BinnedCustomMetric, BinnedCustomMetricStats  } from '$lib/components/monitoring/types';
  import Pill from '../utils/Pill.svelte';
  import { TimeInterval } from '$lib/components/monitoring/types';
  let { 
    metricData = $bindable(),
    currentDriftType = $bindable(),
    currentName = $bindable(),
    currentTimeInterval = $bindable(),
  } = $props<{
    metricData: MetricData;
    currentDriftType: DriftType;
    currentName: string;
    currentTimeInterval: TimeInterval;
  }>();


  // state
  let resetZoom: boolean = $state(false);

  let resetZoomClicked = () => {
    resetZoom = !resetZoom;
  }


  // Helper to get y-values based on drift type
  function getYValues(metricData: MetricData): number[] {
    if (!metricData) return [];
    
    switch (currentDriftType) {
      case DriftType.Spc:
        return (metricData as SpcDriftFeature).values;
      case DriftType.Psi:
        return (metricData as BinnedPsiMetric).psi;
      case DriftType.Custom:
        return (metricData as BinnedCustomMetric).stats.map(
          (stat: BinnedCustomMetricStats) => stat.avg
        );
      default:
        return [];
    }
  }


</script>

<div class="flex flex-col">
  <div class="items-center text-xl mr-2 font-bold text-primary-800">Recent Metrics</div>

  <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full">
    <div class="flex flex-row flex-wrap gap-2 items-center">
      <Pill key="Key" value={currentName} />
      <Pill key="Time Window" value={currentTimeInterval} />
    </div>

    <button class="btn flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
      <div class="text-black">Reset Zoom</div>
    </button>
  </div>

  <TimeSeries
    timestamps={metricData.created_at}
    values={getYValues(metricData)}
    label={currentName}
    yLabel={currentDriftType === DriftType.Psi ? 'PSI Value' : 'Value'}
    bind:resetZoom={resetZoom}
  />
</div>