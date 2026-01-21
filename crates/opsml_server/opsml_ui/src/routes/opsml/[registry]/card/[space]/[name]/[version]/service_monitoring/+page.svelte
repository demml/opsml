<script lang="ts">
  import { Activity, ChevronDown, ChevronUp } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import TimeRangeFilter from '$lib/components/trace/TimeRangeFilter.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import CardMonitoringSection from '$lib/components/card/CardMonitoringSection.svelte';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  
  let selectedDriftType = $state<DriftType>(data.allDriftTypes[0] || DriftType.Custom);
  
  const driftTypeConfig = {
    [DriftType.Custom]: { title: 'Custom Metrics', color: 'bg-emerald-100' },
    [DriftType.GenAI]: { title: 'GenAI', color: 'bg-purple-100' },
    [DriftType.Psi]: { title: 'PSI Distribution', color: 'bg-blue-100' },
    [DriftType.Spc]: { title: 'SPC Charts', color: 'bg-orange-100' },
  };

  let currentConfig = $derived(driftTypeConfig[selectedDriftType]);
  
  // Filter cards that have the currently selected drift type
  let cardsWithSelectedDrift = $derived(
    data.cardMonitoringData.filter(cm => cm.driftTypes.includes(selectedDriftType))
  );

  function handleRangeChange(newRange: any) {
    timeRangeState.updateTimeRange(newRange);
  }

  // Determine grid layout based on card count
  let gridCols = $derived.by(() => {
    const count = cardsWithSelectedDrift.length;
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-1 xl:grid-cols-2';
    return 'grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3';
  });
</script>

<div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 space-y-6">
  <!-- Header with drift type selector -->
  <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl">
    <div class="flex items-center gap-3">
      <div class="p-2 {currentConfig.color} border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        <Activity class="w-6 h-6 text-black" />
      </div>
      <div>
        <h1 class="text-2xl font-black text-black uppercase tracking-tight">
          Service Monitoring
        </h1>
        <p class="text-sm text-gray-600 font-medium">
          {data.metadata.name} · {cardsWithSelectedDrift.length} card{cardsWithSelectedDrift.length !== 1 ? 's' : ''} with {currentConfig.title}
        </p>
      </div>
    </div>

    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full xl:w-auto">
      {#if data.allDriftTypes.length > 1}
        <div class="flex flex-wrap gap-2">
          {#each data.allDriftTypes as type}
            {@const cardCount = data.cardMonitoringData.filter(cm => cm.driftTypes.includes(type)).length}
            <button
              class="btn text-sm font-bold uppercase transition-all duration-150 {type === selectedDriftType ? 'bg-slate-100 border-primary-800 translate-x-[1px] translate-y-[1px] shadow-none text-black' : 'bg-primary-500 text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[-1px] hover:translate-x-[-1px] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'} border-2 border-black rounded-lg px-4 py-2"
              onclick={() => selectedDriftType = type}
            >
              {type} ({cardCount})
            </button>
          {/each}
        </div>
      {/if}

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

  <!-- Grid of all cards' monitoring -->
  {#if cardsWithSelectedDrift.length > 0}
    <div class="grid {gridCols} gap-6">
      {#each cardsWithSelectedDrift as cardData}
        <CardMonitoringSection
          {cardData}
          driftType={selectedDriftType}
        />
      {/each}
    </div>
  {:else}
    <div class="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-gray-300 rounded-xl bg-surface-50">
      <p class="text-lg font-bold text-gray-600">No cards with {currentConfig.title}</p>
      <p class="text-sm text-gray-500 mt-2">Try selecting a different drift type</p>
    </div>
  {/if}
</div>