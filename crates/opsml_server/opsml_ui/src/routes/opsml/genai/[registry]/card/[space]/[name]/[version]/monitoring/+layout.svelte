<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Activity, Brain, Waves, LineChart } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { LayoutData } from './$types';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import { getRegistryPath, getRegistryFromString, RegistryType } from "$lib/utils";

  let { data, children }: { data: LayoutData; children: any } = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  let registryType = $derived(getRegistryFromString(page.params.registry as string)) as RegistryType;


  const driftTypeConfig = {
    [DriftType.Custom]: { title: 'Custom Metrics', icon: Activity, color: 'text-emerald-600', bg: 'bg-emerald-100' },
    [DriftType.GenAI]: { title: 'GenAI', icon: Brain, color: 'text-purple-600', bg: 'bg-purple-100' },
    [DriftType.Psi]: { title: 'PSI Distribution', icon: Waves, color: 'text-blue-600', bg: 'bg-blue-100' },
    [DriftType.Spc]: { title: 'SPC Charts', icon: LineChart, color: 'text-orange-600', bg: 'bg-orange-100' },
  };

  let currentConfig = $derived(driftTypeConfig[DriftType.GenAI]);
  let basePath = $derived(`/opsml/${getRegistryPath(registryType)}/card/${data.metadata.space}/${data.metadata.name}/${data.metadata.version}/monitoring`);

  function handleRangeChange(newRange: any) {
    timeRangeState.updateTimeRange(newRange);
  }
</script>

{#if scouterEnabled}
  <div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 space-y-6">
    <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
      <div class="flex items-center gap-3">
        <div class="p-2 {currentConfig.bg} border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <currentConfig.icon class="w-6 h-6 text-black" />
        </div>
        <h1 class="text-2xl font-black text-black uppercase tracking-tight">
          {currentConfig.title} Dashboard
        </h1>
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
      </div>
    </div>

    {@render children()}
  </div>
{:else}
  <ScouterRequiredView
    featureName="Monitoring Dashboard"
    featureDescription="Gain real-time insights into your model's performance, track key metrics, and receive alerts on anomalies with our comprehensive monitoring dashboard powered by Scouter."
    icon={Activity}
  />
{/if}