<script lang="ts">
  import { onMount } from 'svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import type { MonitoringPageData } from './utils';
  import { refreshMonitoringData } from './utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints } from '$lib/utils';
  import { Loader2 } from 'lucide-svelte';

  // Props
  let { monitoringData = $bindable() }: { monitoringData: Extract<MonitoringPageData, { status: 'success' }> } = $props();

  let selectedDriftType = $state(monitoringData.selectedData.driftType);
  let isRefreshing = $state(false);

  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);

  let driftTypes = $derived(monitoringData.driftTypes);

  onMount(() => {
    currentMaxPoints = getMaxDataPoints();
    let timeoutId: NodeJS.Timeout;

    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const newMax = getMaxDataPoints();
        if (newMax !== currentMaxPoints) {
          currentMaxPoints = newMax;
        }
      }, 400);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  });


  $effect(() => {
    // Capture dependencies
    const type = selectedDriftType;
    const range = monitoringData.selectedTimeRange;
    const points = currentMaxPoints;

    // Guard against SSR execution or uninitialized points
    if (typeof window !== 'undefined' && points > 0) {
       console.log("Triggering Global Context Refresh:", JSON.stringify({ type, range, points }));
       
       // Trigger a full refresh (no cursors implies reset to page 1 for data continuity)
       performRefresh(type); 
    }
  });


  async function performRefresh(
      type: DriftType,
      rCursor?: { cursor: RecordCursor, direction: string },
      wCursor?: { cursor: RecordCursor, direction: string }
  ) {
    isRefreshing = true;
    try {
   
        await refreshMonitoringData(fetch, type, monitoringData, {
            recordCursor: rCursor,
            workflowCursor: wCursor
        });

    } catch (e) {
        console.error("Dashboard Refresh Failed", e);
    } finally {
        isRefreshing = false;
    }
  }

  function handleDriftTypeChange(newType: DriftType) {
      selectedDriftType = newType;
  }


  async function handleRecordPageChange(cursor: RecordCursor, direction: string) {
      console.log("Pagination Event: Record", direction);
      await performRefresh(selectedDriftType, { cursor, direction }, undefined);
  }

  async function handleWorkflowPageChange(cursor: RecordCursor, direction: string) {
      console.log("Pagination Event: Workflow", direction);
      await performRefresh(selectedDriftType, undefined, { cursor, direction });
  }
</script>

<div class="mx-auto w-full max-w-8xl px-4 py-2 sm:px-6 lg:px-8 relative">

  {#if isRefreshing}
    <div class="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg shadow-lg animate-pulse border-2 border-white">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span class="text-xs font-bold uppercase tracking-wider">Syncing...</span>
    </div>
  {/if}

  {#if driftTypes.length > 1}
    <div class="flex flex-wrap gap-2 mb-4 p-4 bg-white rounded-lg border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
      <span class="font-bold text-primary-800 mr-2 flex items-center">DRIFT TYPE:</span>
      {#each driftTypes as type}
        <button
          class="btn text-sm font-bold uppercase transition-all duration-150 {type === selectedDriftType ? 'bg-slate-100 border-primary-800 translate-x-[1px] translate-y-[1px] shadow-none' : 'bg-primary-500 text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[-1px] hover:translate-x-[-1px] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'} border-2 border-black rounded-lg px-4 py-2"
          onclick={() => handleDriftTypeChange(type)}
        >
          {type}
        </button>
      {/each}
    </div>
  {/if}

  {#key selectedDriftType}
    {#if selectedDriftType === DriftType.GenAI}
      <GenAIDashboard
        bind:monitoringData
        onRecordPageChange={handleRecordPageChange}
        onWorkflowPageChange={handleWorkflowPageChange}
      />
    {:else if selectedDriftType === DriftType.Custom}
      <div class="p-8 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
         <h2 class="font-bold text-xl">PSI Dashboard (Coming Soon)</h2>
       </div>
    {:else if selectedDriftType === DriftType.Psi}
       <div class="p-8 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
         <h2 class="font-bold text-xl">PSI Dashboard (Coming Soon)</h2>
       </div>
    {:else if selectedDriftType === DriftType.Spc}
       <div class="p-8 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
         <h2 class="font-bold text-xl">SPC Dashboard (Coming Soon)</h2>
       </div>
    {/if}
  {/key}
</div>