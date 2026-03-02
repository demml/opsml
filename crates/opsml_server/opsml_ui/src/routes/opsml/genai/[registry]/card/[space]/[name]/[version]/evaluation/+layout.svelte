<script lang="ts">
  import { page } from '$app/state';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Activity, Brain, RefreshCw } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { LayoutData } from './$types';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import { getRegistryFromString, RegistryType } from "$lib/utils";

  let { data, children }: { data: LayoutData; children: any } = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  let registryType = $derived(getRegistryFromString(page.params.registry as string)) as RegistryType;
  let isAgent = $derived(registryType === RegistryType.Agent);

  const dashboardTitle = $derived(isAgent ? 'Agent Evaluation Dashboard' : 'GenAI Evaluation Dashboard');

  function handleRangeChange(newRange: any) {
    timeRangeState.updateTimeRange(newRange);
  }
</script>

{#if scouterEnabled}
  <div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 space-y-6">
    <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-purple-100 border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <Brain class="w-6 h-6 text-black" />
        </div>
        <div>
          <h1 class="text-xl font-black text-black uppercase tracking-tight">
            {dashboardTitle}
          </h1>
          {#if isAgent}
            <p class="text-xs text-slate-500 font-mono mt-0.5">
              {data.metadata.name} · v{data.metadata.version}
            </p>
          {/if}
        </div>
      </div>

      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full xl:w-auto">
        <div class="hidden sm:block w-[2px] h-8 bg-black/10 mx-2"></div>
        <div class="w-full sm:w-auto">
          {#if timeRangeState.selectedTimeRange}
            <TimeRangeFilter
              selectedRange={timeRangeState.selectedTimeRange}
              onRangeChange={handleRangeChange}
            />
          {/if}
        </div>
        <button
          onclick={() => timeRangeState.refresh()}
          class="flex items-center gap-2 px-3 py-2 bg-white border-2 border-black rounded-lg shadow-small hover:bg-primary-50 hover:shadow-hover transition-all duration-100 text-sm font-bold text-black"
          title="Refresh data"
          aria-label="Refresh data"
        >
          <RefreshCw class="w-4 h-4" />
        </button>
      </div>
    </div>

    {@render children()}
  </div>
{:else}
  <ScouterRequiredView
    featureName="Evaluation Dashboard"
    featureDescription="Gain real-time insights into your prompt and agent evaluations, track key metrics, and monitor evaluation performance with our comprehensive dashboard powered by Scouter."
    icon={Activity}
  />
{/if}
