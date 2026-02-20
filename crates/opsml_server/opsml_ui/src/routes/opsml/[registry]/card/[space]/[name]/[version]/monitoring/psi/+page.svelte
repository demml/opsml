<script lang="ts">
  import { onMount } from 'svelte';
  import MonitoringErrorView from '$lib/components/scouter/dashboard/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';
  import type { MonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import { refreshMonitoringData, changeAlertPage } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getMaxDataPoints } from '$lib/utils';
  import { Loader2 } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import CustomDashboard from '$lib/components/scouter/custom/CustomDashboard.svelte';
  import PsiDashboard from '$lib/components/scouter/psi/PsiDashboard.svelte';
  import SpcDashboard from '$lib/components/scouter/spc/SpcDashboard.svelte';
  import { acknowledgeMonitoringAlert } from '$lib/components/scouter/alert/utils';
  import { getServerDriftAlerts } from '$lib/components/scouter/utils';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';

  let { data }: PageProps = $props();
  let monitoringData = $state<MonitoringPageData>(data.monitoringData);
  let driftType = $derived(data.driftType);
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
        performRefresh(driftType);
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

  async function performRefresh(type: DriftType) {
    if (monitoringData.status !== 'success') return;
    
    isRefreshing = true;
    try {
      await refreshMonitoringData(fetch, type, monitoringData);
    } catch (e) {
      console.error('Dashboard Refresh Failed', e);
    } finally {
      isRefreshing = false;
    }
  }

  async function handleAlertPageChange(cursor: RecordCursor, direction: string) {
    if (monitoringData.status !== 'success') return;
    
    isRefreshing = true;
    try {
      await changeAlertPage(fetch, { cursor, direction }, monitoringData);
    } catch (e) {
      console.error('Alert Page Change Failed', e);
    } finally {
      isRefreshing = false;
    }
  }

  async function updateAlert(id: number, space: string): Promise<void> {
    if (monitoringData.status !== 'success') return;
    
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

{#if isRefreshing}
  <div class="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg shadow-lg animate-pulse border-2 border-white transition-opacity duration-200">
    <Loader2 class="w-4 h-4 animate-spin" />
    <span class="text-xs font-bold uppercase tracking-wider">Syncing...</span>
  </div>
{/if}

{#if monitoringData.status === 'error'}
  <MonitoringErrorView
    message={monitoringData.errorMsg}
    space={data.metadata.space}
    name={data.metadata.name}
    version={data.metadata.version}
    registryType={data.registryType}
  />
{:else}
  <div class="transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none grayscale-[0.5]' : ''}">
    {#if driftType === DriftType.Custom}
      <CustomDashboard bind:monitoringData onAlertPageChange={handleAlertPageChange} onUpdateAlert={updateAlert} />
    {:else if driftType === DriftType.Psi}
      <PsiDashboard bind:monitoringData onAlertPageChange={handleAlertPageChange} onUpdateAlert={updateAlert} />
    {:else if driftType === DriftType.Spc}
      <SpcDashboard bind:monitoringData onAlertPageChange={handleAlertPageChange} onUpdateAlert={updateAlert} />
    {/if}
  </div>
{/if}