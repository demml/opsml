<script lang="ts">
  import { onMount } from 'svelte';
  import MonitoringErrorView from '$lib/components/scouter/dashboard/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';
  import type { GenAIMonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import { refreshGenAIMonitoringData } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints } from '$lib/utils';
  import { Loader2 } from 'lucide-svelte';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';

  let { data }: PageProps = $props();
  let monitoringData = $state<GenAIMonitoringPageData>(data.monitoringData);
  let isRefreshing = $state(false);
  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);


  $effect(() => {
    const newRange = timeRangeState.selectedTimeRange;

    if (newRange && monitoringData.status === 'success') {
      const currentRange = monitoringData.selectedTimeRange;

      if (
        currentRange.startTime !== newRange.startTime ||
        currentRange.endTime !== newRange.endTime
      ) {
        monitoringData.selectedTimeRange = newRange;
        performRefresh();
      }
    }
  });

  onMount(() => {
    currentMaxPoints = getMaxDataPoints();
    let timeoutId: NodeJS.Timeout;

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
    if (monitoringData.status !== 'success') return;

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

{#if isRefreshing}
  <div class="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg shadow-lg animate-pulse border-2 border-white transition-opacity duration-200">
    <Loader2 class="w-4 h-4 animate-spin" />
    <span class="text-xs font-bold uppercase tracking-wider">Syncing...</span>
  </div>
{/if}

{#if monitoringData.status === 'error'}
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