<script lang="ts">
  import { DashboardContext } from '$lib/components/scouter/dashboard/dashboard.svelte';
  import { createCustomStore } from './metric.svelte';
  
  // Components
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import CustomConfigHeader from './CustomConfigHeader.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';
  
  // Icons & Types
  import { KeySquare, Loader2, Activity } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { MonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import type { BinnedMetrics, CustomDriftProfile } from '$lib/components/scouter/custom/types';

  // 1. Only accept monitoringData
  let { monitoringData }: {
    monitoringData: Extract<MonitoringPageData, { status: 'success' }>;
  } = $props();

  const dashboardCtx = new DashboardContext(monitoringData.selectedTimeRange);

  const profile = monitoringData.profiles[DriftType.Custom].profile.Custom as CustomDriftProfile;
  const config = profile.config;

  const isSsrDataForCustom = monitoringData.selectedData.driftType === DriftType.Custom;
  
  const initialMetrics = isSsrDataForCustom
    ? (monitoringData.selectedData.metrics as BinnedMetrics)
    : null;

  const store = createCustomStore({
    config,
    ctx: dashboardCtx,
    initialMetrics
  });
</script>

<div class="mx-auto w-full px-4 sm:px-6 lg:px-8 space-y-8 pb-12">

  <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-b-4 border-black pb-4 mt-4">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-emerald-100 border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        <Activity class="w-6 h-6 text-black" />
      </div>
      <h1 class="text-2xl font-black text-black uppercase tracking-tight">
        Custom Metrics Dashboard
      </h1>
      {#if store.isLoading}
        <div class="flex items-center gap-2 px-3 py-1 bg-slate-100 border border-black rounded-full transition-all">
            <Loader2 class="w-4 h-4 animate-spin text-primary-600" />
            <span class="text-xs font-bold text-slate-600">Syncing...</span>
        </div>
      {/if}
    </div>
    <div class="w-full sm:w-auto">
      <TimeRangeFilter
        selectedRange={dashboardCtx.timeRange}
        onRangeChange={(range) => dashboardCtx.updateTimeRange(range)}
      />
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

    <div class="lg:col-span-3 flex flex-col gap-6">

      <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl flex flex-col gap-5">
        <div class="flex flex-col gap-2">
          <label for="metric-selector" class="text-xs font-black uppercase text-slate-500 tracking-wider">
            Select Feature
          </label>
          <div class="relative w-full">
            <div class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <KeySquare class="w-4 h-4 text-emerald-600" />
            </div>
            <div class="w-full [&>button]:w-full [&>button]:pl-9 [&>button]:text-left">
                <ComboBoxDropDown
                  boxId="metric-selector"
                  bind:defaultValue={store.currentMetricName}
                  boxOptions={store.availableMetricNames}
                />
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
        <CustomConfigHeader
          config={config}
          alertConfig={config.alert_config}
          profile={profile}
          profileUri={monitoringData.profiles[DriftType.Custom].profile_uri}
          uid={config.uid}
          registry={monitoringData.registryType}
        />
      </div>
    </div>

    <div class="lg:col-span-9 h-full min-h-[500px]">
      <div class="h-full bg-white border-2 border-black p-0 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl flex flex-col overflow-hidden">
        <div class="px-4 py-3 border-b-2 border-black bg-slate-50 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-emerald-500 border border-black"></div>
            <h2 class="font-bold text-lg text-slate-900">Feature Analysis</h2>
          </div>
          <span class="text-xs font-mono font-bold bg-black text-white px-3 py-1 rounded-md shadow-sm">
            {store.currentMetricName || 'NO SELECTION'}
          </span>
        </div>

        <div class="flex-grow relative bg-white p-4">
          {#if store.isLoading && !store.currentMetricData}
             <div class="absolute inset-0 flex items-center justify-center bg-white/80 z-10 backdrop-blur-sm">
                <Loader2 class="w-10 h-10 animate-spin text-emerald-600" />
             </div>
          {/if}

          {#if store.currentMetricData}
            {#key store.currentMetricName}
              <VizBody
                metricData={store.currentMetricData}
                currentDriftType={DriftType.Custom}
                currentName={store.currentMetricName}
                currentConfig={config}
                currentProfile={profile}
              />
            {/key}
          {:else}
            <div class="flex flex-col items-center justify-center h-full text-slate-400 font-mono text-sm border-2 border-dashed border-slate-200 rounded-lg p-4">
              <KeySquare class="w-10 h-10 mb-3 opacity-30"/>
              <span>Select a feature to view drift metrics</span>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>