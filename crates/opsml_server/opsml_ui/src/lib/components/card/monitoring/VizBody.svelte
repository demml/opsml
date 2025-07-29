
<script lang="ts">
  import TimeSeries from '$lib/components/viz/TimeSeries.svelte';
  import 'chartjs-adapter-date-fns';
  import { DriftType } from '$lib/components/card/monitoring/types';
  import 'chartjs-adapter-date-fns';
  import type { MetricData, SpcDriftFeature, BinnedPsiMetric, BinnedMetric, BinnedMetricStats  } from '$lib/components/card/monitoring/types';
  import Pill from '$lib/components/utils/Pill.svelte';
  import { TimeInterval } from '$lib/components/card/monitoring/types';
  import { type DriftConfigType } from './util';
  import CustomAlertPill from '$lib/components/card/monitoring/custom/CustomAlertPill.svelte';
  import { getCustomAlertCondition, type CustomMetricDriftConfig } from './custom/custom';
  import { type DriftProfile } from './util';

  let { 
    metricData,
    currentDriftType,
    currentName,
    currentTimeInterval,
    currentConfig,
    currentProfile,
  } = $props<{
    metricData: MetricData;
    currentDriftType: DriftType;
    currentName: string;
    currentTimeInterval: TimeInterval;
    currentConfig: DriftConfigType;
    currentProfile: DriftProfile;

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
      return [...(metricData as SpcDriftFeature).values];
    case DriftType.Psi:
      return [...(metricData as BinnedPsiMetric).psi];
    case DriftType.Custom:
      return [...(metricData as BinnedMetric).stats.map(
        (stat: BinnedMetricStats) => stat.avg
      )];
    default:
      return [];
  }
}

function getBaselineValue(): number | undefined {
  // get custom value
  if (currentConfig && currentDriftType === DriftType.Custom) {
      return (currentProfile as DriftProfile).Custom.metrics[currentName];
  }

  // get psi threshold
  if (currentDriftType === DriftType.Psi) {
    const psiProfile = (currentProfile as DriftProfile).Psi;
    const threshold = psiProfile.config.alert_config.threshold;
    if (threshold) {
    
      if (threshold.Normal) {
        return threshold.Normal.alpha;
      } else if (threshold.ChiSquare) {
      return threshold.ChiSquare.alpha;
      } else if (threshold.Fixed) {
        return threshold.Fixed.threshold;
      }
    }
    return undefined;
  }

  return undefined;
}

</script>

<div class="flex flex-col">
  <div class="items-center text-lg mr-2 font-bold text-primary-800">Recent Metrics</div>

  <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full px-2">
    <div class="flex flex-row flex-wrap gap-2 items-center">
      <Pill key="Key" value={currentName} textSize="text-sm"/>
      <Pill key="drift" value={currentDriftType} textSize="text-sm"/>
      <Pill key="Time Window" value={currentTimeInterval} textSize="text-sm"/>

      {#if currentConfig && currentDriftType === DriftType.Custom}
        {@const alertInfo = getCustomAlertCondition(currentConfig as CustomMetricDriftConfig, currentName)}
        {@const metricValue = (currentProfile as DriftProfile).Custom.metrics[currentName]}
        {#if alertInfo}
          <CustomAlertPill 
            value={metricValue}
            alertInfo={alertInfo}
           />
        {/if}
      {/if}
    </div>

    <button class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg self-center" onclick={() => resetZoomClicked()}>
      <div class="text-black">Reset Zoom</div>
    </button>
  </div>

  {#key metricData}
    <TimeSeries
        timestamps={metricData.created_at}
        values={getYValues(metricData)}
        baselineValue={getBaselineValue()}
        label={currentName}
        yLabel={currentDriftType === DriftType.Psi ? 'PSI Value' : 'Value'}
        bind:resetZoom={resetZoom}
      />
  {/key}

 


</div>