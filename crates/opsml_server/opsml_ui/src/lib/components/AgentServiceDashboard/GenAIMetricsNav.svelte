<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import DashboardTimeBar from '$lib/components/utils/DashboardTimeBar.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte.ts';
  import { type TimeRange } from '$lib/components/trace/types';
  import { type Writable } from 'svelte/store';

  const dispatch = createEventDispatcher();

  export let selected: string = 'overview';
  export let models: string[] = [];
  export let providers: string[] = [];

  let modelFilter: string | null = null;
  let providerFilter: string | null = null;

  function selectKey(key: string) {
    selected = key;
    dispatch('select', { key });
  }

  function applyFilters() {
    dispatch('filters', { model: modelFilter, provider: providerFilter });
  }

  function onRangeChange(range: TimeRange) {
    timeRangeState.updateTimeRange(range);
    dispatch('rangeChange', { range });
  }

  function onRefresh() {
    timeRangeState.refresh();
    dispatch('refresh');
  }
</script>

<div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl space-y-4">
  <div>
    <h4 class="text-xs font-black uppercase tracking-wide text-primary-900">GenAI Metrics</h4>
    <p class="text-[11px] text-primary-600 mt-1">Select a view and adjust range/filters</p>
  </div>

  <div>
    <nav aria-label="GenAI metrics navigation" class="flex flex-col gap-2">
      <button
        class="flex items-center justify-between px-3 py-2 text-sm font-black uppercase tracking-wide border-2 rounded-base transition-all duration-100 {selected === 'overview' ? 'bg-primary-800 text-white border-black' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        on:click={() => selectKey('overview')}
      >
        Overview
      </button>

      <button
        class="flex items-center justify-between px-3 py-2 text-sm font-black uppercase tracking-wide border-2 rounded-base transition-all duration-100 {selected === 'by_model' ? 'bg-primary-800 text-white border-black' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        on:click={() => selectKey('by_model')}
      >
        By Model
      </button>

      <button
        class="flex items-center justify-between px-3 py-2 text-sm font-black uppercase tracking-wide border-2 rounded-base transition-all duration-100 {selected === 'token_usage' ? 'bg-primary-800 text-white border-black' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        on:click={() => selectKey('token_usage')}
      >
        Token Usage
      </button>

      <button
        class="flex items-center justify-between px-3 py-2 text-sm font-black uppercase tracking-wide border-2 rounded-base transition-all duration-100 {selected === 'latency' ? 'bg-primary-800 text-white border-black' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
        on:click={() => selectKey('latency')}
      >
        Latency
      </button>
    </nav>
  </div>

  <div>
    <DashboardTimeBar
      selectedRange={timeRangeState.selectedTimeRange}
      refreshing={timeRangeState.isRefreshing}
      onRangeChange={(e) => onRangeChange(e.detail)}
      onRefresh={onRefresh}
    />
  </div>

  <div class="space-y-2">
    <label class="text-xs font-black uppercase text-primary-700 flex flex-col">
      <span class="mb-1">Model filter</span>
      <input
        class="flex-1 px-2 py-1 border-2 border-black rounded-base bg-surface-50 text-sm"
        placeholder="Filter by model"
        bind:value={modelFilter}
        on:input={applyFilters}
      />
    </label>
  </div>

  <div class="space-y-2">
    <label class="text-xs font-black uppercase text-primary-700 flex flex-col">
      <span class="mb-1">Provider filter</span>
      <select
        class="w-full px-2 py-1 border-2 border-black rounded-base bg-surface-50 text-sm"
        bind:value={providerFilter}
        on:change={applyFilters}
      >
        <option value="">All providers</option>
        {#each providers as p}
          <option value={p}>{p} (provider)</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="pt-2 border-t-2 border-black flex items-center justify-between">
    <small class="text-xs text-primary-600">Auto-refresh: live</small>
    <button
      class="px-3 py-1.5 bg-surface-50 border-2 border-black rounded-base text-sm font-black hover:bg-primary-100"
      on:click={() => { timeRangeState.refresh(); dispatch('refresh'); }}
    >
      Refresh
    </button>
  </div>
</div>

<style>
  :global(.rounded-base) { border-radius: 0.375rem; }
</style>
