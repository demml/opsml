<script lang="ts">
  import type { GenAIEvalConfig, GenAIEvalProfile, GenAIEvalRecordPaginationResponse, GenAIEvalWorkflowPaginationResponse } from '../types';
  import type { GenAIMonitoringPageData } from '../../dashboard/utils';
  import type { RecordCursor } from '../../types';
  import type { BinnedMetrics } from '../../custom/types';
  import { DriftType } from '$lib/components/scouter/types';

  // Components
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import GenAIConfigHeader from '../GenAIConfigHeader.svelte';
  import GenAIEvalRecordTable from '../record/GenAIEvalRecordTable.svelte';
  import GenAIEvalWorkflowTable from '../workflow/GenAIEvalWorkflowTable.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';

  // Icons
  import { KeySquare, TableProperties, ArrowRightLeft } from 'lucide-svelte';

  // Props
  let {
    monitoringData = $bindable(),
    onRecordPageChange,
    onWorkflowPageChange
  }: {
    monitoringData: Extract<GenAIMonitoringPageData, { status: 'success' }>;
    onRecordPageChange: (cursor: RecordCursor, direction: string) => Promise<void>;
    onWorkflowPageChange: (cursor: RecordCursor, direction: string) => Promise<void>;
  } = $props();

  // -- Derived Data from Parent --
  const profile = $derived(monitoringData.profile as GenAIEvalProfile);
  const config = $derived(profile.config as GenAIEvalConfig);

  const records = $derived(monitoringData.selectedData.records ?? { items: [], has_next: false, has_prev: false });
  const workflows = $derived(monitoringData.selectedData.workflows ?? { items: [], has_next: false, has_prev: false });

  const metrics = $derived(monitoringData.selectedData.metrics as { task: BinnedMetrics; workflow: BinnedMetrics });
  const taskMetrics = $derived(metrics?.task);
  const workflowMetrics = $derived(metrics?.workflow);

  let selectedMetricView = $state<'task' | 'workflow'>('workflow');
  let currentMetricName = $state<string>('');

  const currentMetricsObj = $derived(selectedMetricView === 'task' ? taskMetrics : workflowMetrics);
  const availableMetricNames = $derived(currentMetricsObj?.metrics ? Object.keys(currentMetricsObj.metrics) : []);
  const currentMetricData = $derived(currentMetricsObj && currentMetricName ? currentMetricsObj.metrics[currentMetricName] : null);

  $effect(() => {
    if (availableMetricNames.length > 0 && !availableMetricNames.includes(currentMetricName)) {
      currentMetricName = availableMetricNames[0];
    }
  });


  const metricViews = ['task', 'workflow'] as const;
</script>

<div class="mx-auto w-full px-4 sm:px-6 lg:px-8 space-y-8 pb-12">
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
    <div class="lg:col-span-3 flex flex-col gap-6">
      <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl flex flex-col gap-5">
        <div class="flex flex-col gap-2">
            <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Metric Type</span>
            <div class="flex p-1 bg-slate-100 border-2 border-black rounded-lg gap-1">
            {#each metricViews as viewType}
                <button
                class="flex-1 px-3 py-2 text-sm font-bold rounded-md border-2 transition-all duration-200
                    {viewType === selectedMetricView
                    ? 'bg-primary-500 text-white border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] translate-x-[-1px] translate-y-[-1px]'
                    : 'bg-white text-slate-700 border-transparent hover:border-slate-300 hover:bg-slate-50'}"
                onclick={() => selectedMetricView = viewType}
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
                  bind:defaultValue={currentMetricName}
                  boxOptions={availableMetricNames}
                />
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
        <GenAIConfigHeader
          config={config}
          alertConfig={config.alert_config}
          profile={profile}
          profileUri={monitoringData.profileUri}
          uid={config.uid}
          registry={monitoringData.registryType}
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
            {currentMetricName || 'NO SELECTION'}
          </span>
        </div>
        <div class="flex-grow relative bg-white p-4">
          {#if currentMetricData}
            {#key currentMetricName}
              <VizBody
                metricData={currentMetricData}
                currentDriftType={DriftType.GenAI}
                currentName={currentMetricName}
                currentConfig={config}
                currentProfile={profile}
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

  <div class="grid grid-cols-1 gap-6">

    {#if records && records.items && records.items.length > 0}
      <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
        <div class="bg-primary-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
          <h3 class="font-black text-lg uppercase tracking-tight flex items-center gap-2 text-slate-900">
            <TableProperties class="w-5 h-5" />
            Evaluation Records
          </h3>
          <span class="text-xs font-bold bg-black text-white px-2 py-0.5 rounded-full border border-black">
            {records.items.length}
          </span>
        </div>

        <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
           {#key records}
              <GenAIEvalRecordTable
                currentPage={records as GenAIEvalRecordPaginationResponse}
                onPageChange={onRecordPageChange}
              />
           {/key}
        </div>
      </div>
    {/if}

    {#if workflows && workflows.items && workflows.items.length > 0}
      <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
        <div class="bg-purple-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
          <h3 class="font-black text-lg uppercase tracking-tight flex items-center gap-2 text-slate-900">
            <ArrowRightLeft class="w-5 h-5" />
            Workflow Results
          </h3>
          <span class="text-xs font-bold bg-black text-white px-2 py-0.5 rounded-full border border-black">
            {workflows.items.length}
          </span>
        </div>

        <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
            {#key workflows}
                <GenAIEvalWorkflowTable
                  currentPage={workflows as GenAIEvalWorkflowPaginationResponse}
                  onPageChange={onWorkflowPageChange}
                  profile={profile}
                />
            {/key}
        </div>
      </div>
    {/if}
  </div>
</div>