<script lang="ts">
  import { page } from '$app/state';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Activity, Brain } from 'lucide-svelte';
  import type { LayoutData } from './$types';
  import DashboardTimeBar from '$lib/components/utils/DashboardTimeBar.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import { getRegistryFromString, RegistryType } from "$lib/utils";
  import type { TimeRange } from '$lib/components/trace/types';
  import { setCookie } from '$lib/components/trace/utils';

  let { data, children }: { data: LayoutData; children: any } = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  let mockMode = $derived(data.mockMode ?? false);
  let registryType = $derived(getRegistryFromString(page.params.registry as string)) as RegistryType;
  let isAgent = $derived(registryType === RegistryType.Agent);

  const dashboardTitle = $derived(isAgent ? 'Agent Evaluation Dashboard' : 'Prompt Evaluation Dashboard');

  function handleRangeChange(newRange: TimeRange) {
    timeRangeState.updateTimeRange(newRange);
    setCookie('monitoring_range', newRange.value);
  }
</script>

{#if scouterEnabled || mockMode}
  <div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 space-y-6">
    <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow rounded-base">
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

      {#if timeRangeState.selectedTimeRange}
        <DashboardTimeBar
          selectedRange={timeRangeState.selectedTimeRange}
          refreshing={timeRangeState.isRefreshing}
          onRangeChange={handleRangeChange}
          onRefresh={() => timeRangeState.refresh()}
        />
      {/if}
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
