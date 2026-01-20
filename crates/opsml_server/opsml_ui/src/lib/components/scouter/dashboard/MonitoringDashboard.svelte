<script lang="ts">
  import { onMount } from 'svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import type { MonitoringPageData } from './utils';
  import { changeAlertPage, refreshMonitoringData } from './utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints } from '$lib/utils';
  import { Loader2, Activity, Brain, Waves, LineChart } from 'lucide-svelte';
  import CustomDashboard from '../custom/CustomDashboard.svelte';
  import { acknowledgeMonitoringAlert } from '../alert/utils';
  import { getServerDriftAlerts } from '../utils';
  import PsiDashboard from '../psi/PsiDashboard.svelte';
  import SpcDashboard from '../spc/SpcDashboard.svelte';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';

  // Props
  let { monitoringData = $bindable() }: { monitoringData: Extract<MonitoringPageData, { status: 'success' }> } = $props();

  let selectedDriftType = $state(monitoringData.selectedData.driftType);
  let isRefreshing = $state(false);
  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);
  let driftTypes = $derived(monitoringData.driftTypes);

  const dashboardConfig = {
    [DriftType.Custom]: { title: 'Custom Metrics Dashboard', icon: Activity, color: 'text-emerald-600', bg: 'bg-emerald-100' },
    [DriftType.GenAI]:  { title: 'GenAI Dashboard', icon: Brain, color: 'text-purple-600', bg: 'bg-purple-100' },
    [DriftType.Psi]:    { title: 'PSI Distribution', icon: Waves, color: 'text-blue-600', bg: 'bg-blue-100' },
    [DriftType.Spc]:    { title: 'SPC Charts', icon: LineChart, color: 'text-orange-600', bg: 'bg-orange-100' },
  };

  let currentConfig = $derived(dashboardConfig[selectedDriftType] || { title: 'Dashboard', icon: Activity, color: 'text-gray-600', bg: 'bg-gray-100' });

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
      if (selectedDriftType === newType) return;
      if (typeof window !== 'undefined' && currentMaxPoints > 0) {
        performRefresh(newType);
      };

      selectedDriftType = monitoringData.selectedData.driftType;

  }

  function handleRangeChange(newRange: any) {
     monitoringData.selectedTimeRange = newRange;
     performRefresh(selectedDriftType);
  }

  async function handleRecordPageChange(cursor: RecordCursor, direction: string) {
      await performRefresh(selectedDriftType, { cursor, direction }, undefined);
  }
  
  async function handleWorkflowPageChange(cursor: RecordCursor, direction: string) {
      await performRefresh(selectedDriftType, undefined, { cursor, direction });
  }
  
  async function handleAlertPageChange(cursor: RecordCursor, direction: string) {
      isRefreshing = true;
      try {
          await changeAlertPage(fetch, { cursor, direction }, monitoringData);
      } catch (e) {
          console.error("Dashboard Refresh Failed", e);
      } finally {
          isRefreshing = false;
      }
  }
  
  async function updateAlert(id: number, space: string): Promise<void> {
    const updated = await acknowledgeMonitoringAlert(fetch, id, space);
    if (updated) {
      const newAlerts = await getServerDriftAlerts(fetch, {
        uid: monitoringData.selectedData.profile.config.uid,
        active: true,
        start_datetime: monitoringData.selectedTimeRange.startTime,
        end_datetime: monitoringData.selectedTimeRange.endTime,
      });
      monitoringData.selectedData.driftAlerts = newAlerts;
    }
  }
</script>

<div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 relative overflow-x-hidden space-y-6">

  {#if isRefreshing}
    <div class="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg shadow-lg animate-pulse border-2 border-white transition-opacity duration-200">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span class="text-xs font-bold uppercase tracking-wider">Syncing...</span>
    </div>
  {/if}

  <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
    <div class="flex items-center gap-3">
        <div class="p-2 {currentConfig.bg} border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            <currentConfig.icon class="w-6 h-6 text-black" />
        </div>
        <h1 class="text-2xl font-black text-black uppercase tracking-tight">
            {currentConfig.title}
        </h1>
    </div>

    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full xl:w-auto">
        {#if driftTypes.length > 1}
            <div class="flex flex-wrap gap-2">
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
        <div class="hidden sm:block w-[2px] h-8 bg-black/10 mx-2"></div>
        <div class="w-full sm:w-auto">
             <TimeRangeFilter
                selectedRange={monitoringData.selectedTimeRange}
                onRangeChange={handleRangeChange}
            />
        </div>
    </div>
  </div>

  <div class="transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none grayscale-[0.5]' : ''}">
      {#key selectedDriftType}
        {#if selectedDriftType === DriftType.GenAI}
          <GenAIDashboard
            bind:monitoringData
            onRecordPageChange={handleRecordPageChange}
            onWorkflowPageChange={handleWorkflowPageChange}
          />
        {:else if selectedDriftType === DriftType.Custom}
          <CustomDashboard
            bind:monitoringData
            onAlertPageChange={handleAlertPageChange}
            onUpdateAlert={updateAlert}
          />
        {:else if selectedDriftType === DriftType.Psi}
           <PsiDashboard
            bind:monitoringData
            onAlertPageChange={handleAlertPageChange}
            onUpdateAlert={updateAlert}
          />
        {:else if selectedDriftType === DriftType.Spc}
           <SpcDashboard
            bind:monitoringData
            onAlertPageChange={handleAlertPageChange}
            onUpdateAlert={updateAlert}
          />
        {/if}
      {/key}
  </div>
</div>