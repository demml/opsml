<script lang="ts">

  // Components
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import ComboBoxDropDown from '$lib/components/utils/ComboBoxDropDown.svelte';
  import SpcConfigHeader from './SpcConfigHeader.svelte';
  import VizBody from '$lib/components/scouter/dashboard/VizBody.svelte';

  // Icons & Types
  import { KeySquare, Activity, Siren } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { MonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import SpcAlertTable from '$lib/components/scouter/spc/SpcAlertTable.svelte';
  import type { BinnedSpcFeatureMetrics, SpcDriftConfig, SpcDriftProfile } from './types';

  // Props
  let {
    monitoringData = $bindable(),
    onAlertPageChange,
    onUpdateAlert
  }: {
    monitoringData: Extract<MonitoringPageData, { status: 'success' }>;
    onAlertPageChange: (cursor: RecordCursor, direction: string) => Promise<void>;
    onUpdateAlert: (id: number, space: string) => Promise<void>;
  } = $props();

  let currentMetricName = $state<string>('');

  // Derived
  const profile = $derived(monitoringData.profiles[DriftType.Spc].profile.Spc as SpcDriftProfile);
  const config = $derived(profile.config as SpcDriftConfig);
  const metrics = $derived(monitoringData.selectedData.metrics as BinnedSpcFeatureMetrics);

  // Drift Alerts Data
  const driftAlerts = $derived(monitoringData.selectedData.driftAlerts);

  const availableMetricNames = $derived(metrics?.features ? Object.keys(metrics.features) : []);
  const currentMetricData = $derived(currentMetricName ? metrics?.features[currentMetricName] : null);

  console.log('SPC Dashboard - currentMetricData:', JSON.stringify(currentMetricData, null, 2));

  // Auto-select first metric if none selected
  $effect(() => {
    if (availableMetricNames.length > 0 && !currentMetricName) {
      currentMetricName = availableMetricNames[0];
    }
  });

  function handleRangeChange(newRange: any) {
     monitoringData.selectedTimeRange = newRange;
  }
</script>

<div class="mx-auto w-full space-y-8 pb-12">

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
                  bind:defaultValue={currentMetricName}
                  boxOptions={availableMetricNames}
                />
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
        <SpcConfigHeader
          config={config}
          alertConfig={config.alert_config}
          profile={profile}
          profileUri={monitoringData.profiles[DriftType.Spc].profile_uri}
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
                currentDriftType={DriftType.Spc}
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

  <div class="max-w-2/3 min-w-0 mx-auto">
     {#if driftAlerts && driftAlerts.items}
      <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
        <div class="bg-error-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
          <h3 class="font-black text-lg uppercase tracking-tight flex items-center gap-2 text-slate-900">
            <Siren class="w-5 h-5 text-error-700" />
            System Alerts
          </h3>
          <span class="text-xs font-bold bg-black text-white px-2 py-0.5 rounded-full border border-black">
            {driftAlerts.items.length}
          </span>
        </div>

        <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
           <SpcAlertTable
             {driftAlerts}
             onPageChange={onAlertPageChange}
             {onUpdateAlert}
             space={config.space}
           />
        </div>
      </div>
     {/if}
  </div>

</div>

