<script lang="ts">
  import { DriftType } from '$lib/components/scouter/types';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import type { MonitoringPageData } from './utils';


  let { monitoringData }: { monitoringData: Extract<MonitoringPageData, { status: 'success' }> } = $props();
  let selectedDriftType = $state(monitoringData.selectedData.driftType);
  let driftTypes = $derived(monitoringData.driftTypes);

</script>

<div class="mx-auto w-full max-w-8xl px-4 py-2 sm:px-6 lg:px-8">

  {#if driftTypes.length > 1}
    <div class="flex flex-wrap gap-2 mb-4 p-4 bg-white rounded-lg border-2 border-black shadow">
      <span class="font-bold text-primary-800 mr-2">Drift Type:</span>
      {#each driftTypes as type}
        <button
          class="btn text-sm {type === selectedDriftType ? 'bg-slate-100 border-primary-800' : 'bg-primary-500 shadow shadow-hover'} border-2 border-black rounded-lg px-4 py-2"
          onclick={() => selectedDriftType = type}
        >
          {type}
        </button>
      {/each}
    </div>
  {/if}

  {#key selectedDriftType }
    <!-- Load dashboard based on drift type -->
    {#if selectedDriftType === DriftType.GenAI}
      <GenAIDashboard
        monitoringData={monitoringData}
      />
    {/if}
    


  {/key}

  <!--
  {#if selectedDriftType === DriftType.GenAI && isGenAIConfig(currentData.config)}
    <GenAIDashboard
      {uid}
      config={currentData.config as GenAIEvalConfig}
      profile={currentData.profile}
      {profiles}
      {initialTimeRange}
      initialRecords={rest.genAIEvalRecords}
      initialWorkflows={rest.genAIEvalWorkflows}
    />
   <!--{:else if [DriftType.Spc, DriftType.Psi, DriftType.Custom].includes(selectedDriftType) && (isSpcConfig(currentData.config) || isPsiConfig(currentData.config) || isCustomConfig(currentData.config))}
    <MetricDashboard
      {uid}
      driftType={selectedDriftType}
      profile={currentData.profile}
      config={currentData.config}
      {profiles}
      {initialTimeRange}
      initialMetrics={rest.initialMetrics}
      initialAlerts={rest.driftAlerts}
      {registryType}
    />
  -->

</div>