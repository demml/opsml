<script lang="ts">
  import type { BinnedDriftMap, LLMPageResponse, MetricData } from '$lib/components/card/monitoring/types';
  import { DriftType, TimeInterval } from '$lib/components/card/monitoring/types';
  import type { DriftProfileResponse, UiProfile, DriftConfigType } from '$lib/components/card/monitoring/utils';
  import type { Alert } from '$lib/components/card/monitoring/alert/types';
  import VizBody from '$lib/components/card/monitoring/VizBody.svelte';
  import Header from '$lib/components/card/monitoring/Header.svelte';
  import AlertTable from '$lib/components/card/monitoring/alert/AlertTable.svelte';
  import { getMaxDataPoints, debounce } from '$lib/utils';
  import type { RegistryType } from '$lib/utils';
  import {
    getCurrentMetricData,
    getLatestMonitoringMetrics,
    getMonitoringAlerts,
    getProfileFeatures,
    getProfileConfig,
  } from '$lib/components/card/monitoring/utils';
  import LLMRecordTable from './llm/LLMRecordTable.svelte';
  import { acknowledgeMonitoringAlert } from '$lib/components/card/monitoring/alert/utils';
  import { onMount, onDestroy } from 'svelte';

  /**
   * Props for the monitoring dashboard component
   */
  interface Props {
    /** Profile data for drift monitoring */
    profiles: DriftProfileResponse;
    /** Available drift types */
    driftTypes: DriftType[];
    /** Initial configuration */
    initialName: string;
    initialNames: string[];
    initialDriftType: DriftType;
    initialProfile: UiProfile;
    initialMetrics: BinnedDriftMap;
    initialMetricData: MetricData;
    initialMaxDataPoints: number;
    initialConfig: DriftConfigType;
    initialAlerts: Alert[];
    /** Metadata */
    uid: string;
    registryType: RegistryType;
    /** Initial time interval, defaults to 6 hours */
    initialTimeInterval?: TimeInterval;
    currentLLMRecords?: LLMPageResponse;
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
    initialAlerts,
    uid,
    registryType,
    initialTimeInterval = TimeInterval.SixHours,
    currentLLMRecords
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
  let currentAlerts = $state(initialAlerts);
  let currentTimeInterval = $state(initialTimeInterval);
  let currentLLMRecordPage = $state(currentLLMRecords);

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
        currentTimeInterval,
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

  /**
   * Handles time interval change and refreshes data
   */
  async function handleTimeChange(timeInterval: TimeInterval): Promise<void> {
    currentTimeInterval = timeInterval;
    
    // Fetch updated metrics
    latestMetrics = await getLatestMonitoringMetrics(
      fetch,
      profiles,
      currentTimeInterval,
      currentMaxDataPoints
    );

    currentMetricData = getCurrentMetricData(
      latestMetrics,
      currentDriftType,
      currentName
    );

    // Fetch updated alerts
    currentAlerts = await getMonitoringAlerts(
      fetch,
      currentConfig.uid,
      currentTimeInterval,
      true
    );
  }

  /**
   * Updates alert acknowledgment status
   */
  async function updateAlert(id: number, space: string): Promise<void> {
    const updated = await acknowledgeMonitoringAlert(fetch, id, space);

    if (updated) {
      currentAlerts = await getMonitoringAlerts(
        fetch,
        currentConfig.uid,
        currentTimeInterval,
        true
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
        bind:currentTimeInterval
        bind:currentName
        {currentNames}
        {currentConfig}
        {currentProfile}
        {handleDriftTypeChange}
        {handleNameChange}
        {handleTimeChange}
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
            {currentTimeInterval}
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
          name={currentConfig.name}
          version={currentConfig.version}
          currentPage={currentLLMRecordPage}
        />
      </div>
    {/if}
  </div>
</div>