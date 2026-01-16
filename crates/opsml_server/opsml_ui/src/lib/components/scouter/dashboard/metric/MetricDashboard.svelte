<script lang="ts">
  import { DriftType } from '$lib/components/scouter/types';
  import type { DriftConfigType, UiProfile, DriftProfileResponse  } from '$lib/components/scouter/utils';
  import type { BaseProfileDashboardProps } from '$lib/components/scouter/dashboard/types';
  import { isCustomConfig, isPsiConfig, isSpcConfig } from '$lib/components/scouter/utils';
  import { MetricDashboardState } from './MetricDashboardState.svelte';
  import DashboardLifecycle from '$lib/components/scouter/dashboard/DashboardLifecycle.svelte';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';
  import AlertTable from '$lib/components/scouter/alert/AlertTable.svelte';
  import { acknowledgeMonitoringAlert } from '$lib/components/scouter/alert/utils';
  import { getServerDriftAlerts } from '$lib/components/scouter/utils';
  import { KeySquare } from 'lucide-svelte';
  import CustomConfigHeader from '$lib/components/scouter/custom/CustomConfigHeader.svelte';
  import PsiConfigHeader from '$lib/components/scouter/psi/PsiConfigHeader.svelte';
  import SpcConfigHeader from '$lib/components/scouter/spc/SpcConfigHeader.svelte';
  import type { RegistryType } from '$lib/utils';
  import type { BinnedDriftMap } from '$lib/components/scouter/types';
  import type { DriftAlertPaginationResponse } from '$lib/components/scouter/alert/types';


  interface Props extends BaseProfileDashboardProps {
    driftType: DriftType;
    profile: UiProfile;
    config: DriftConfigType;
    profiles: DriftProfileResponse;
    initialMetrics: BinnedDriftMap;
    initialAlerts: DriftAlertPaginationResponse;
    registryType: RegistryType;
  }

  let {
    uid,
    driftType,
    profile,
    config,
    profiles,
    initialTimeRange,
    initialMetrics,
    initialAlerts,
    registryType
  }: Props = $props();

  const state = new MetricDashboardState({
    driftType,
    profile,
    config,
    profiles,
    initialMetrics,
    initialTimeRange,
    initialAlerts,
  });

  async function updateAlert(id: number, space: string): Promise<void> {
    const updated = await acknowledgeMonitoringAlert(fetch, id, space);
    if (updated && state.selectedTimeRange) {
      state.driftAlerts = await getServerDriftAlerts(fetch, {
        uid: config.uid,
        active: true,
        start_datetime: state.selectedTimeRange.startTime,
        end_datetime: state.selectedTimeRange.endTime,
      });
    }
  }
</script>

<DashboardLifecycle {state} />

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 gap-4">
    <!-- Header Section -->
    <div class="flex flex-wrap gap-4">
      <!-- Config Info -->
      <div class="bg-white p-4 rounded-lg shadow border-2 border-black w-fit">
        {#if isCustomConfig(config)}
          <CustomConfigHeader
            {config}
            alertConfig={config.alert_config}
            {profile}
            {uid}
            registry={registryType}
          />
        {:else if isPsiConfig(config)}
          <PsiConfigHeader
            {config}
            alertConfig={config.alert_config}
            {profile}
            {uid}
            registry={registryType}
          />
        {:else if isSpcConfig(config)}
          <SpcConfigHeader
            {config}
            alertConfig={config.alert_config}
            {profile}
            {uid}
            registry={registryType}
          />
        {/if}
      </div>

      <!-- Filters -->
      <div class="flex flex-col justify-center p-4 bg-white rounded-lg border-2 border-black shadow w-fit">
        <div class="flex flex-row gap-3">
          <div class="flex flex-col gap-2 text-primary-800">
            <span class="font-bold">Time Range:</span>
            <TimeRangeFilter
              selectedRange={state.selectedTimeRange}
              onRangeChange={(range) => state.handleTimeRangeChange(range)}
            />
          </div>

          <div class="flex flex-col gap-2 text-primary-800">
            <span class="font-bold">Metric:</span>
            <div class="flex flex-row gap-1">
              <div class="self-center">
                <KeySquare color="#5948a3" />
              </div>
              <ComboBoxDropDown
                boxId="metric-selector"
                defaultValue={state.currentName}
                boxOptions={state.availableNames}
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Visualization -->
    <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[30rem]">
      {#if state.currentMetricData}
        <VizBody
          metricData={state.currentMetricData}
          currentDriftType={driftType}
          currentName={state.currentName}
          currentConfig={config}
          currentProfile={profile.profile}
        />
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          No data available for selected metric
        </div>
      {/if}
    </div>

    <!-- Alerts Table -->
    {#if state.driftAlerts && state.driftAlerts.items.length > 0}
      <div class="bg-white p-2 border-2 border-black rounded-lg shadow">
        <AlertTable
          driftAlerts={state.driftAlerts}
          {updateAlert}
          onPageChange={(cursor, direction) => state.handleAlertPageChange(cursor, direction)}
        />
      </div>
    {/if}
  </div>
</div>