<!--
  PromptEvalDashboard.svelte
  ──────────────────────────
  Evaluation dashboard for a single prompt card. Handles time-range refresh,
  record/workflow page navigation, and renders AgentDashboard or the error view.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import MonitoringErrorView from '$lib/components/scouter/dashboard/MonitoringErrorView.svelte';
  import type { AgentMonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import { refreshAgentMonitoringData } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints, type RegistryType } from '$lib/utils';
  import AgentDashboard from '$lib/components/scouter/agent/dashboard/AgentDashboard.svelte';
  import AgentTaskAccordion from '$lib/components/scouter/agent/task/AgentTaskAccordion.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';

  let {
    initialMonitoringData,
    metadata,
    registryType,
  }: {
    initialMonitoringData: AgentMonitoringPageData;
    metadata: { name: string; space: string; version: string };
    registryType: RegistryType;
  } = $props();

  let monitoringData = $state<AgentMonitoringPageData>(initialMonitoringData);
  let isRefreshing = $state(false);
  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);
  // Snapshot on mount so stale singleton state from prior navigation never triggers an immediate refresh.
  let lastSeenRange = $state(timeRangeState.selectedTimeRange);
  let lastSeenSignal = $state(timeRangeState.refreshSignal);

  $effect(() => {
    if (isRefreshing) return;
    const newRange = timeRangeState.selectedTimeRange;
    const signal = timeRangeState.refreshSignal;
    if (newRange && monitoringData?.status === 'success') {
      const rangeChanged =
        lastSeenRange.startTime !== newRange.startTime ||
        lastSeenRange.endTime !== newRange.endTime;
      const signalFired = signal !== lastSeenSignal;
      if (rangeChanged || signalFired) {
        lastSeenRange = newRange;
        lastSeenSignal = signal;
        monitoringData.selectedTimeRange = newRange;
        performRefresh();
      }
    }
  });

  onMount(() => {
    currentMaxPoints = getMaxDataPoints();
    let timeoutId: ReturnType<typeof setTimeout>;
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const newMax = getMaxDataPoints();
        if (newMax !== currentMaxPoints) currentMaxPoints = newMax;
      }, 400);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  });

  async function performRefresh(
    rCursor?: { cursor: RecordCursor; direction: string },
    wCursor?: { cursor: RecordCursor; direction: string }
  ) {
    if (!monitoringData || monitoringData.status !== 'success') return;
    isRefreshing = true;
    timeRangeState.beginRefresh();
    try {
      await refreshAgentMonitoringData(fetch, monitoringData, {
        recordCursor: rCursor,
        workflowCursor: wCursor,
      });
    } catch (e) {
      console.error('Agent Dashboard Refresh Failed', e);
    } finally {
      isRefreshing = false;
      timeRangeState.endRefresh();
    }
  }

  async function handleRecordPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh({ cursor, direction }, undefined);
  }

  async function handleWorkflowPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh(undefined, { cursor, direction });
  }
</script>

{#if monitoringData.status === 'error'}
  <AgentTaskAccordion tasks={monitoringData.profile.tasks} />
  <MonitoringErrorView
    message={monitoringData.errorMsg}
    errorKind={monitoringData.errorKind}
    space={metadata.space}
    name={metadata.name}
    version={metadata.version}
    {registryType}
  />
{:else if monitoringData.status === 'success'}
  <div class="transition-opacity duration-200 {isRefreshing ? 'opacity-60 grayscale-[0.5]' : ''}">
    <AgentDashboard
      bind:monitoringData
      onRecordPageChange={handleRecordPageChange}
      onWorkflowPageChange={handleWorkflowPageChange}
    />
  </div>
{/if}
