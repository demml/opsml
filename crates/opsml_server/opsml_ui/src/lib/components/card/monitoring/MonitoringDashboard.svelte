<script lang="ts">
  import type { BinnedDriftMap, MetricData } from '$lib/components/card/monitoring/types';
  import { DriftType } from '$lib/components/card/monitoring/types';
  import type { DriftProfileResponse, UiProfile, DriftConfigType } from '$lib/components/card/monitoring/utils';
  import type { DriftAlertPaginationResponse } from '$lib/components/card/monitoring/alert/types';
  import type { TimeRange } from '$lib/components/trace/types';
  import VizBody from '$lib/components/card/monitoring/VizBody.svelte';
  import Header from '$lib/components/card/monitoring/Header.svelte';
  import AlertTable from '$lib/components/card/monitoring/alert/AlertTable.svelte';
  import { getMaxDataPoints, debounce } from '$lib/utils';
  import type { RegistryType } from '$lib/utils';
  import {
    getCurrentMetricData,
    getLatestMonitoringMetrics,
    getServerDriftAlerts,
    getProfileFeatures,
    getProfileConfig,
  } from '$lib/components/card/monitoring/utils';
  import LLMRecordTable from './llm/LLMRecordTable.svelte';
  import { acknowledgeMonitoringAlert } from '$lib/components/card/monitoring/alert/utils';
  import { onMount, onDestroy } from 'svelte';
  import type { LLMDriftRecordPaginationResponse } from './llm/llm';


  /**
   * Props for the monitoring dashboard component
   */
  interface Props {
    profiles: DriftProfileResponse;
    driftTypes: DriftType[];
    initialName: string;
    initialNames: string[];
    initialDriftType: DriftType;
    initialProfile: UiProfile;
    initialMetrics: BinnedDriftMap;
    initialMetricData: MetricData;
    initialMaxDataPoints: number;
    initialConfig: DriftConfigType;
    uid: string;
    registryType: RegistryType;
    initialTimeRange: TimeRange;
    driftAlerts?: DriftAlertPaginationResponse;
    llmDriftRecords?: LLMDriftRecordPaginationResponse;
  }

  let {
    profiles,
    driftTypes,
    initialName,
    initialNames,
    initialDriftType,
    initialProfile,
    initialMetrics,
    initialMetricData,
    initialMaxDataPoints,
    initialConfig,
    uid,
    registryType,
    initialTimeRange,
    driftAlerts,
    llmDriftRecords
  }: Props = $props();

  // Reactive state using runes
  let currentName = $state(initialName);
  let currentNames = $state(initialNames);
  let currentDriftType = $state(initialDriftType);
  let currentProfile = $state(initialProfile);
  let latestMetrics = $state(initialMetrics);
  let currentMetricData = $state(initialMetricData);
  let currentMaxDataPoints = $state(initialMaxDataPoints);
  let currentConfig = $state(initialConfig);
  let currentDriftAlerts = $state(driftAlerts);
  let selectedTimeRange = $state<TimeRange>(initialTimeRange);
  let currentLLMDriftRecords = $state(llmDriftRecords);
  let isUpdating = $state(false);

  /**
   * Checks screen size and updates metrics if data points threshold changes
   */
  async function checkScreenSize(): Promise<void> {
    const newMaxDataPoints = getMaxDataPoints();
    if (newMaxDataPoints !== currentMaxDataPoints) {
      currentMaxDataPoints = newMaxDataPoints;

      latestMetrics = await getLatestMonitoringMetrics(
        fetch,
        profiles,
        selectedTimeRange,
        currentMaxDataPoints
      );

      currentMetricData = getCurrentMetricData(
        latestMetrics,
        currentDriftType,
        currentName
      );
    }
  }

  const debouncedCheckScreenSize = debounce(checkScreenSize, 400);

  /**
   * Handles drift type selection change
   */
  function handleDriftTypeChange(driftType: DriftType): void {
    currentDriftType = driftType;
    currentProfile = profiles[driftType];

    // Update available names for the new drift type
    currentNames = getProfileFeatures(currentDriftType, currentProfile.profile);

    // Set the first available name as default
    currentName = currentNames[0];

    // Update configuration for the new drift type
    currentConfig = getProfileConfig(currentDriftType, currentProfile.profile);

    // Update metric data with new drift type and name
    currentMetricData = getCurrentMetricData(
      latestMetrics,
      currentDriftType,
      currentName
    );
  }

  /**
   * Handles metric name selection change
   */
  function handleNameChange(name: string): void {
    currentName = name;
    currentMetricData = getCurrentMetricData(
      latestMetrics,
      currentDriftType,
      currentName
    );
  }

  async function handleTimeRangeChange(range: TimeRange): Promise<void> {
    if (isUpdating) return;
    isUpdating = true;

    try {
      selectedTimeRange = range;

      latestMetrics = await getLatestMonitoringMetrics(
        fetch,
        profiles,
        range,
        currentMaxDataPoints,
      );

      currentMetricData = getCurrentMetricData(
        latestMetrics,
        currentDriftType,
        currentName
      );

    } catch (error) {
      console.error('Failed to update time range:', error);
    } finally {
      isUpdating = false;
    }
  }

  /**
   * Updates alert acknowledgment status
   */
  async function updateAlert(id: number, space: string): Promise<void> {
    const updated = await acknowledgeMonitoringAlert(fetch, id, space);

    if (updated) {
      currentDriftAlerts = await getServerDriftAlerts(
        fetch,
        {
          uid: currentConfig.uid,
          active: true
        }
      );
    }
  }

  // Lifecycle management
  onMount(() => {
    window.addEventListener('resize', debouncedCheckScreenSize);
  });

  onDestroy(() => {
    window.removeEventListener('resize', debouncedCheckScreenSize);
  });
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 gap-4 pt-4">

    <!-- Header Section -->
    <div class="h-fit">
      <Header
        availableDriftTypes={driftTypes}
        {currentDriftType}
        bind:selectedTimeRange
        bind:currentName
        {currentNames}
        {currentConfig}
        {currentProfile}
        {handleDriftTypeChange}
        {handleNameChange}
        {handleTimeRangeChange}
        {uid}
        registry={registryType}
      />
    </div>

    <!-- Visualization Section -->
    <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[30rem]">
      {#if currentName && latestMetrics}
        {#if currentMetricData}
          <VizBody
            metricData={currentMetricData}
            {currentDriftType}
            {currentName}
            {currentConfig}
            currentProfile={currentProfile.profile}
          />
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500">
            No data available for selected metric
          </div>
        {/if}
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          Select a metric to view data
        </div>
      {/if}
    </div>

    <!-- Alerts Section -->
    <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[6rem] max-h-[30rem]">
      <AlertTable
        alerts={currentAlerts}
        {updateAlert}
      />
    </div>

    <!-- If LLM records are available -->
    {#if currentLLMRecordPage}
      <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[6rem]">
        <LLMRecordTable
          space={currentConfig.space}
          uid={currentConfig.uid}
          currentPage={currentLLMRecordPage}
        />
      </div>
    {/if}
  </div>
</div>