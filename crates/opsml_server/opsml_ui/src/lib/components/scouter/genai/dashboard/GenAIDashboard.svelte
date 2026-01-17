<script lang="ts">
  import type { GenAIEvalConfig, GenAIEvalRecordPaginationResponse, GenAIEvalWorkflowPaginationResponse } from '../types';
  import type { BaseProfileDashboardProps } from '$lib/components/scouter/dashboard/types';
  import type { DriftProfileResponse, UiProfile } from '$lib/components/scouter/utils';
  import { GenAIDashboardState } from './GenAIDashboardState.svelte';
  import DashboardLifecycle from '$lib/components/scouter/dashboard/DashboardLifecycle.svelte';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import GenAIConfigHeader from '../GenAIConfigHeader.svelte';
  import GenAIEvalRecordTable from '../record/GenAIEvalRecordTable.svelte';
  import GenAIEvalWorkflowTable from '../workflow/GenAIEvalWorkflowTable.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';
  import { RegistryType } from '$lib/utils';
  import { KeySquare } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { BinnedMetrics } from '../../custom/types';

  interface Props extends BaseProfileDashboardProps {
    config: GenAIEvalConfig;
    profile: UiProfile;
    profiles: DriftProfileResponse;
    initialRecords: GenAIEvalRecordPaginationResponse;
    initialWorkflows: GenAIEvalWorkflowPaginationResponse;
    initialMetrics: { task: BinnedMetrics, workflow: BinnedMetrics };
  }

  let {
    uid,
    config,
    profile,
    profiles,
    initialTimeRange,
    initialRecords,
    initialWorkflows,
    initialMetrics,
  }: Props = $props();

  const state = new GenAIDashboardState({
    config,
    profiles,
    initialTimeRange,
    initialRecords,
    initialWorkflows,
    initialMetrics,
  });
</script>

<DashboardLifecycle {state} />

<div class="mx-auto w-full max-w-8xl px-4 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold text-primary-800">GenAI Evaluation Dashboard</h1>
    <div class="flex justify-end">
      <TimeRangeFilter
        selectedRange={state.selectedTimeRange}
        onRangeChange={(range) => state.handleTimeRangeChange(range)}
      />
    </div>
  </div>

  <div class="grid grid-cols-1 gap-4">
    <!-- Header Section -->
    <div class="flex flex-wrap gap-4">
      <!-- Filters Container -->
      <div class="flex flex-col justify-center p-4 bg-white rounded-lg border-2 border-black shadow w-fit">
        <!-- Metric View Selector Row -->
        <div class="flex flex-row flex-wrap gap-2 items-center justify-start mb-4">
          <span class="items-start mr-1 font-bold text-primary-800">Metric View:</span>
          {#each ['task', 'workflow'] as viewType}
            {#if viewType === state.selectedMetricView}
              <button class="btn text-sm flex items-center gap-2 bg-slate-100 border-primary-800 border-2 rounded-lg px-4 py-2">
                <div class="text-primary-800">{viewType}</div>
              </button>
            {:else}
              <button
                class="btn text-sm flex items-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg px-4 py-2" 
                onclick={() => state.selectedMetricView = viewType}
              >
                <div class="text-black">{viewType}</div>
              </button>
            {/if}
          {/each}
        </div>

        {#key state.currentMetrics}
          <div class="flex gap-3 items-center">
            <span class="font-bold text-primary-800">Metric:</span>
            <div class="flex gap-2 items-center">
              <KeySquare color="#5948a3" />
              <ComboBoxDropDown
                boxId="metric-selector"
                defaultValue={state.currentMetricName}
                boxOptions={state.availableMetricNames}
              />
            </div>
          </div>
        {/key}
      </div>

      <!-- Config Info -->
      <div class="bg-white p-4 rounded-lg border-2 border-black shadow w-fit">
        <GenAIConfigHeader
          {config}
          alertConfig={config.alert_config}
          {profile}
          {uid}
          registry={RegistryType.Prompt}
        />
      </div>
    </div>

    <!-- Metrics Visualization -->
    <div class="bg-white p-4 border-2 border-black rounded-lg shadow min-h-[30rem]">
      {#if state.currentMetricData}
        {#key state.currentMetricName}
          <VizBody
            metricData={state.currentMetricData}
            currentDriftType={DriftType.GenAI}
            currentName={state.currentMetricName}
            currentConfig={config}
            currentProfile={profile.profile}
          />
        {/key}
      {:else if state.currentMetrics}
        <div class="flex items-center justify-center h-full text-gray-500">
          {state.currentMetricName ? 'No data available for selected metric' : 'Select a metric to view data'}
        </div>
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          No metrics available for current time range
        </div>
      {/if}
    </div>

    <!-- Tables -->
    <div class="grid grid-cols-1 gap-4">
      {#if state.evalRecords}
        <div class="bg-white p-4 border-2 border-black rounded-lg shadow">
          <h3 class="text-lg font-bold text-primary-800 mb-3">Evaluation Records</h3>
          <GenAIEvalRecordTable
            currentPage={state.evalRecords}
            onPageChange={(cursor, direction) => state.handleRecordPageChange(cursor, direction)}
          />
        </div>
      {/if}

      {#if state.evalWorkflows}
        <div class="bg-white p-4 border-2 border-black rounded-lg shadow">
          <h3 class="text-lg font-bold text-primary-800 mb-3">Workflow Results</h3>
          <GenAIEvalWorkflowTable
            currentPage={state.evalWorkflows}
            onPageChange={(cursor, direction) => state.handleWorkflowPageChange(cursor, direction)}
          />
        </div>
      {/if}
    </div>
  </div>
</div>