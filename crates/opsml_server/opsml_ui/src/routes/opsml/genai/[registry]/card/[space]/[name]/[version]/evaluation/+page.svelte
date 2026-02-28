<script lang="ts">
  import { onMount } from 'svelte';
  import MonitoringErrorView from '$lib/components/scouter/dashboard/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';
  import type { GenAIMonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import { refreshGenAIMonitoringData } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints, RegistryType } from '$lib/utils';
  import { Loader2 } from 'lucide-svelte';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import GenAITaskAccordion from '$lib/components/scouter/genai/task/GenAITaskAccordion.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import AgentEvalDashboard from '$lib/components/card/agent/evaluation/AgentEvalDashboard.svelte';

  let { data }: PageProps = $props();
  let isAgent = $derived(data.registryType === RegistryType.Agent);

  // ── Prompt-only state ──
  let monitoringData = $state<GenAIMonitoringPageData | undefined>(
    data.registryType !== RegistryType.Agent ? (data.monitoringData as GenAIMonitoringPageData) : undefined
  );
  let isRefreshing = $state(false);
  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);
  let lastSeenSignal = $state(timeRangeState.refreshSignal);

  $effect(() => {
    if (isAgent) return;
    if (isRefreshing) return;
    const newRange = timeRangeState.selectedTimeRange;
    const signal = timeRangeState.refreshSignal;
    if (newRange && monitoringData?.status === 'success') {
      const currentRange = monitoringData.selectedTimeRange;
      const rangeChanged =
        currentRange.startTime !== newRange.startTime ||
        currentRange.endTime !== newRange.endTime;
      const signalFired = signal !== lastSeenSignal;
      if (rangeChanged || signalFired) {
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
    try {
      await refreshGenAIMonitoringData(fetch, monitoringData, {
        recordCursor: rCursor,
        workflowCursor: wCursor,
      });
    } catch (e) {
      console.error('GenAI Dashboard Refresh Failed', e);
    } finally {
      isRefreshing = false;
    }
  }

  async function handleRecordPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh({ cursor, direction }, undefined);
  }

  async function handleWorkflowPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh(undefined, { cursor, direction });
  }
</script>

<!-- ── Agent evaluation dashboard ── -->
{#if isAgent}
  <AgentEvalDashboard
    agentName={data.metadata.name}
    agentVersion={data.metadata.version}
    agentPromptEvals={data.agentPromptEvals ?? []}
  />

<!-- ── Prompt evaluation dashboard (unchanged) ── -->
{:else if monitoringData}
  {#if isRefreshing}
    <div class="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg shadow-lg animate-pulse border-2 border-white transition-opacity duration-200">
      <Loader2 class="w-4 h-4 animate-spin" />
      <span class="text-xs font-bold uppercase tracking-wider">Syncing...</span>
    </div>
  {/if}

  {#if monitoringData.status === 'error'}
    <GenAITaskAccordion tasks={monitoringData.profile.tasks} />
    <MonitoringErrorView
      message={monitoringData.errorMsg}
      errorKind={monitoringData.errorKind}
      space={data.metadata.space}
      name={data.metadata.name}
      version={data.metadata.version}
      registryType={data.registryType}
    />
  {:else}
    <div class="transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none grayscale-[0.5]' : ''}">
      <GenAIDashboard
        bind:monitoringData
        onRecordPageChange={handleRecordPageChange}
        onWorkflowPageChange={handleWorkflowPageChange}
      />
    </div>
  {/if}
{/if}
