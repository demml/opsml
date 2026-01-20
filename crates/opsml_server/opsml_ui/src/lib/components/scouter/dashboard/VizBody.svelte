<script lang="ts">
  import TimeSeries from '$lib/components/viz/TimeSeries.svelte';
  import { DriftType } from '../types';
  import type { MetricData } from '../types';
  import { type SpcDriftFeature } from '$lib/components/scouter/spc/types';
  import { type BinnedPsiMetric, type PsiDriftProfile } from '$lib/components/scouter/psi/types';
  import type { BinnedMetric, BinnedMetricStats, CustomDriftProfile} from '$lib/components/scouter/custom/types';
  import Pill from '$lib/components/utils/Pill.svelte';
  import type { DriftConfigType, DriftProfile } from '../utils';
  import CustomAlertPill from '../custom/CustomAlertPill.svelte';
  import GenAIAlertPill from '../genai/AlertPill.svelte';
  import type { CustomMetricDriftConfig } from '../custom/types';
  import { getCustomAlertCondition } from '../custom/utils';
  import type { AlertCondition } from '../types';
  import type { GenAIEvalConfig, GenAIEvalProfile } from '../genai/types';

  let {
    metricData,
    currentDriftType,
    currentName,
    currentConfig,
    currentProfile,
  } = $props<{
    metricData: MetricData;
    currentDriftType: DriftType;
    currentName: string;
    currentConfig: DriftConfigType;
    currentProfile: DriftProfile[DriftType];
  }>();

  let resetZoomTrigger = $state(0);

  function resetZoomClicked() {
    resetZoomTrigger++;
  }

  function getYValues(data: MetricData): number[] {
    if (!data) return [];

    switch (currentDriftType) {
      case DriftType.Spc:
        return [...(data as SpcDriftFeature).values];
      case DriftType.Psi:
        return [...(data as BinnedPsiMetric).psi];
      case DriftType.Custom:
      case DriftType.GenAI:
        return [...(data as BinnedMetric).stats.map((stat: BinnedMetricStats) => stat.avg)];
      default:
        return [];
    }
  }

  function getBaselineValue(): number | undefined {
    if (currentDriftType === DriftType.Custom) {
      return (currentProfile as CustomDriftProfile).metrics[currentName];
    }

    if (currentDriftType === DriftType.GenAI) {
      const alertConfig = (currentProfile as GenAIEvalProfile).config.alert_config.alert_condition;
      return alertConfig?.baseline_value;
    }

    if (currentDriftType === DriftType.Psi) {
      const psiProfile = (currentProfile as PsiDriftProfile);
      const threshold = psiProfile.config.alert_config.threshold;

      if (threshold?.Normal) return threshold.Normal.alpha;
      if (threshold?.ChiSquare) return threshold.ChiSquare.alpha;
      if (threshold?.Fixed) return threshold.Fixed.threshold;
    }

    return undefined;
  }

  const yLabel = $derived(() => {
    if (currentDriftType === DriftType.Psi) return 'PSI Value';
    if (currentDriftType === DriftType.GenAI) return 'Task/Workflow Metric';
    return 'Value';
  });
</script>

<div class="flex flex-col gap-2">
  <div class="text-lg font-bold text-primary-800">Recent Metrics</div>

  <div class="flex flex-row flex-wrap gap-2 pb-2 items-center justify-between w-full px-2">
    <div class="flex flex-row flex-wrap gap-2 items-center">
      <Pill key="Key" value={currentName} textSize="text-sm"/>
      <Pill key="Drift Type" value={currentDriftType} textSize="text-sm"/>

      {#if currentDriftType === DriftType.Custom}
        {@const alertInfo = getCustomAlertCondition(currentConfig as CustomMetricDriftConfig, currentName)}
        {@const metricValue = (currentProfile as CustomDriftProfile).metrics[currentName]}
        {#if alertInfo}
          <CustomAlertPill value={metricValue} {alertInfo} />
        {/if}
      {:else if currentDriftType === DriftType.GenAI}
        {@const alertInfo = (currentConfig as GenAIEvalConfig).alert_config.alert_condition as AlertCondition}
        {#if alertInfo}
          <GenAIAlertPill {alertInfo} />
        {/if}
      {/if}
    </div>

    <button
      class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg"
      onclick={resetZoomClicked}
    >
      <span class="text-white font-bold">Reset Zoom</span>
    </button>
  </div>

  {#key metricData}
    <TimeSeries
      timestamps={metricData.created_at}
      values={getYValues(metricData)}
      baselineValue={getBaselineValue()}
      label={currentName}
      yLabel={yLabel()}
      bind:resetZoomTrigger
    />
  {/key}
</div>