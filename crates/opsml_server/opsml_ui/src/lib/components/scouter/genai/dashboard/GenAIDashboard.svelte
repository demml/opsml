<script lang="ts">
  import type { GenAIEvalConfig, GenAIEvalProfile, GenAIEvalRecordPaginationResponse, GenAIEvalWorkflowPaginationResponse, GenAIAlertConfig } from '../types';
  import { DashboardContext } from '$lib/components/scouter/dashboard/dashboard.svelte';
  import { createGenAIStore } from './genai.svelte';

  // Components
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import GenAIConfigHeader from '../GenAIConfigHeader.svelte';
  import GenAIEvalRecordTable from '../record/GenAIEvalRecordTable.svelte';
  import GenAIEvalWorkflowTable from '../workflow/GenAIEvalWorkflowTable.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';
  import { RegistryType } from '$lib/utils';
  import { KeySquare, Loader2, LayoutDashboard, TableProperties, ArrowRightLeft } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { BinnedMetrics } from '../../custom/types';
  import type { MonitoringPageData } from '../../dashboard/utils';

  let { monitoringData }: { monitoringData: Extract<MonitoringPageData, { status: 'success' }> } = $props();

  const dashboardCtx = new DashboardContext(monitoringData.selectedTimeRange);
  const { selectedData } = monitoringData;

  }: Props = $props();

  const state = new GenAIDashboardState({
    config,
    initialTimeRange,
    initialRecords,
    initialWorkflows,
    initialMetrics,
    config: monitoringData.selectedData.profile.config as GenAIEvalConfig,
    ctx: dashboardCtx,
    initialData: {
      records: monitoringData.selectedData.genAIData?.records as GenAIEvalRecordPaginationResponse,
      workflows: monitoringData.selectedData.genAIData?.workflows as GenAIEvalWorkflowPaginationResponse,
      metrics: { task: genAiMetrics!.task, workflow: genAiMetrics!.workflow }
    }
  });

  const metricViews = ['task', 'workflow'] as const;
</script>

<div class="mx-auto w-full px-4 sm:px-6 lg:px-8 space-y-8 pb-12">

  <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-b-4 border-black pb-4 mt-4">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-primary-100 border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        <LayoutDashboard class="w-6 h-6 text-black" />
      </div>
      <h1 class="text-3xl font-black text-black uppercase tracking-tight">
        GenAI Evaluation
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
            <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Metric Type</span>
            <div class="flex p-1 bg-slate-100 border-2 border-black rounded-lg gap-1">
            {#each metricViews as viewType}
                <button
                class="flex-1 px-3 py-2 text-sm font-bold rounded-md border-2 transition-all duration-200
                    {viewType === store.selectedMetricView
                    ? 'bg-primary-500 text-white border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] translate-x-[-1px] translate-y-[-1px]'
                    : 'bg-white text-slate-700 border-transparent hover:border-slate-300 hover:bg-slate-50'}"
                onclick={() => store.selectedMetricView = viewType}
                >
                {viewType.toUpperCase()}
                </button>
            {/each}
            </div>
        </div>

        <div class="flex flex-col gap-2">
          <label for="metric-selector" class="text-xs font-black uppercase text-slate-500 tracking-wider">
            Select Metric
          </label>
          <div class="relative w-full">
            <div class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <KeySquare class="w-4 h-4 text-primary-600" />
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
        <GenAIConfigHeader
          config={selectedData.profile.config as GenAIEvalConfig}
          alertConfig={selectedData.profile.config.alert_config as GenAIAlertConfig}
          profile={selectedData.profile as GenAIEvalProfile}
          profileUri={selectedData.profileUri}
          uid={selectedData.profile.config.uid}
          registry={RegistryType.Prompt}
        />
      </div>
    </div>

    <div class="lg:col-span-9 h-full min-h-[500px]">
      <div class="h-full bg-white border-2 border-black p-0 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl flex flex-col overflow-hidden">
        <div class="px-4 py-3 border-b-2 border-black bg-slate-50 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-green-500 border border-black"></div>
            <h2 class="font-bold text-lg text-slate-900">Metric Visualization</h2>
          </div>
          <span class="text-xs font-mono font-bold bg-black text-white px-3 py-1 rounded-md shadow-sm">
            {store.currentMetricName || 'NO SELECTION'}
          </span>
        </div>
        <div class="flex-grow relative bg-white p-4">
          {#if store.isLoading && !store.currentMetricData}
             <div class="absolute inset-0 flex items-center justify-center bg-white/80 z-10 backdrop-blur-sm">
                <Loader2 class="w-10 h-10 animate-spin text-primary-600" />
             </div>
          {/if}
          {#if store.currentMetricData}
            {#key store.currentMetricName}
              <VizBody
                metricData={store.currentMetricData}
                currentDriftType={DriftType.GenAI}
                currentName={store.currentMetricName}
                currentConfig={monitoringData.selectedData.profile.config as GenAIEvalConfig}
                currentProfile={monitoringData.selectedData.profile}
              />
            {/key}
          {:else}
            <div class="flex flex-col items-center justify-center h-full text-slate-400 font-mono text-sm border-2 border-dashed border-slate-200 rounded-lg p-4">
              <KeySquare class="w-10 h-10 mb-3 opacity-30"/>
              <span>Select a metric from the sidebar to view data</span>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 2xl:grid-cols-2 gap-6">
    
    {#if store.records}
      <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
        <div class="bg-primary-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
          <h3 class="font-black text-lg uppercase tracking-tight flex items-center gap-2 text-slate-900">
            <TableProperties class="w-5 h-5" />
            Evaluation Records
          </h3>
          <span class="text-xs font-bold bg-black text-white px-2 py-0.5 rounded-full border border-black">
            {store.records.items?.length || 0}
          </span>
        </div>
        
        <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
           {#key store.records}
              <GenAIEvalRecordTable
                currentPage={store.records}
                onPageChange={store.handleRecordPageChange}
              />
           {/key}
        </div>
      </div>
    {/if}

    {#if store.workflows}
      <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
        <div class="bg-purple-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
          <h3 class="font-black text-lg uppercase tracking-tight flex items-center gap-2 text-slate-900">
            <ArrowRightLeft class="w-5 h-5" />
            Workflow Results
          </h3>
          <span class="text-xs font-bold bg-black text-white px-2 py-0.5 rounded-full border border-black">
            {store.workflows.items?.length || 0}
          </span>
        </div>
        
        <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
            {#key store.workflows}
                <GenAIEvalWorkflowTable
                  currentPage={store.workflows}
                  onPageChange={store.handleWorkflowPageChange}
                />
            {/key}
        </div>
      </div>
    {/if}
  </div>
</div>