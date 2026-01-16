<script lang="ts">
  import type { GenAIEvalConfig, GenAIEvalRecordPaginationResponse, GenAIEvalWorkflowPaginationResponse } from '$lib/components/scouter/genai/types';
  import type { BaseProfileDashboardProps } from '$lib/components/scouter/dashboard/types';
  import type { DriftProfileResponse } from '$lib/components/scouter/utils';
  import { GenAIDashboardState } from './GenAIDashboardState.svelte';
  import DashboardLifecycle from '$lib/components/scouter/dashboard/DashboardLifecycle.svelte';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import GenAIConfigHeader from '../GenAIConfigHeader.svelte';
  import GenAIEvalRecordTable from '../record/GenAIEvalRecordTable.svelte';
  import GenAIEvalWorkflowTable from '../workflow/GenAIEvalWorkflowTable.svelte';
  import TaskDetailView from '../task/TaskDetailView.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';
  import type { UiProfile } from '$lib/components/scouter/utils';
  import { RegistryType } from '$lib/utils';
  import { KeySquare, BarChart3 } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';

  interface Props extends BaseProfileDashboardProps {
    config: GenAIEvalConfig;
    profile: UiProfile;
    profiles: DriftProfileResponse;
    initialRecords: GenAIEvalRecordPaginationResponse;
    initialWorkflows: GenAIEvalWorkflowPaginationResponse;
  }

  let {
    uid,
    config,
    profile,
    profiles,
    initialTimeRange,
    initialRecords,
    initialWorkflows
  }: Props = $props();

  const state = new GenAIDashboardState({
    config,
    profiles,
    initialTimeRange,
    initialRecords,
    initialWorkflows,
  });

  const selectedTaskData = $derived(() => {
    if (!state.selectedTask || !state.workflowTasks) return null;
    return state.workflowTasks.tasks.find(t => t.task_id === state.selectedTask);
  });

  const currentMetrics = $derived(() => {
    return state.selectedMetricView === 'task'
      ? state.taskMetrics
      : state.workflowMetrics;
  });
</script>

<DashboardLifecycle {state} />

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 gap-4">
    <!-- Header Section -->
    <div class="flex flex-wrap gap-4">
      <!-- Config Info -->
      <div class="bg-white p-4 rounded-lg shadow border-2 border-black w-fit">
        <GenAIConfigHeader
          {config}
          alertConfig={config.alert_config}
          {profile}
          {uid}
          registry={RegistryType.Prompt}
        />
      </div>

      <!-- Time Range Selector -->
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
            <span class="font-bold">Metric View:</span>
            <div class="flex flex-row gap-1">
              <div class="self-center">
                <BarChart3 color="#5948a3" />
              </div>
              <ComboBoxDropDown
                boxId="metric-view-selector"
                defaultValue={state.selectedMetricView}
                boxOptions={['task', 'workflow']}
              />
            </div>
          </div>

          {#if currentMetrics()}
            <div class="flex flex-col gap-2 text-primary-800">
              <span class="font-bold">Metric:</span>
              <div class="flex flex-row gap-1">
                <div class="self-center">
                  <KeySquare color="#5948a3" />
                </div>
                <ComboBoxDropDown
                  boxId="metric-name-selector"
                  defaultValue={state.currentMetricName}
                  boxOptions={state.availableMetricNames}
                />
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Metrics Visualization -->
    {#if currentMetrics() && state.currentMetricData}
      <div class="bg-white p-2 border-2 border-black rounded-lg shadow min-h-[30rem]">
        <VizBody
          metricData={state.currentMetricData}
          currentDriftType={DriftType.GenAI}
          currentName={state.currentMetricName}
          currentConfig={config}
          currentProfile={profile.profile}
        />
      </div>
    {/if}

    <!-- Main Content Grid: Tables & Task Details -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Left Column: Records & Workflows -->
      <div class="flex flex-col gap-4">
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

      <!-- Right Column
      <div class="bg-white p-4 border-2 border-black rounded-lg shadow min-h-[600px]">
        <h3 class="text-lg font-bold text-primary-800 mb-3">Task Details</h3>
        {#if selectedTaskData()}
          <TaskDetailView
            task={selectedTaskData()}
            allTasks={state.workflowTasks?.tasks ?? []}
          />
        {:else if state.workflowTasks}
          <div class="flex items-center justify-center h-full text-gray-500">
            Select a task to view details
          </div>
        {:else}
          <div class="flex items-center justify-center h-full text-gray-500">
            Select a record or workflow to view tasks
          </div>
        {/if}
      </div>
      : Task Details -->
    </div>
  </div>
</div>