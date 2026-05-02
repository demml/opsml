<script lang="ts">
  import VariantA from '$lib/components/dev/agentMetricsMocks/TraceVariantA_Compact.svelte';
  import VariantB from '$lib/components/dev/agentMetricsMocks/TraceVariantB_Debugger.svelte';
  import VariantC from '$lib/components/dev/agentMetricsMocks/TraceVariantC_Waterfall.svelte';
  import { buildTraceMockResponse } from '$lib/components/dev/agentMetricsMocks/traceMockData';

  type VariantKey = 'A' | 'B' | 'C';
  let active = $state<VariantKey>('A');

  const data = buildTraceMockResponse();

  const tabs: { key: VariantKey; label: string; sub: string }[] = [
    { key: 'A', label: 'A · Compact', sub: 'KPI + charts + inspector' },
    { key: 'B', label: 'B · Debugger', sub: 'Filterable list + big detail' },
    { key: 'C', label: 'C · Waterfall', sub: 'Gantt timeline + detail' }
  ];
</script>

<div class="min-h-screen bg-surface-100 p-4">
  <div class="max-w-[1600px] mx-auto space-y-4">
    <div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="text-[10px] font-black uppercase tracking-widest text-primary-600">DEV / SANDBOX</div>
          <h1 class="text-2xl font-black text-black uppercase tracking-tight">Trace Metrics Mocks</h1>
          <p class="text-xs font-mono text-gray-700 mt-1">
            TraceDetailContent &gt; Metrics tab · GenAiTraceMetricsResponse · 10-span research_agent trace
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          {#each tabs as t}
            <button
              type="button"
              onclick={() => (active = t.key)}
              class="px-3 py-2 border-2 border-black rounded-base text-xs font-black uppercase tracking-wide transition-colors duration-100 {active === t.key
                ? 'bg-primary-500 text-white shadow'
                : 'bg-surface-50 text-primary-800 shadow-small hover:bg-primary-100'}"
            >
              <div>{t.label}</div>
              <div class="text-[9px] font-mono opacity-80">{t.sub}</div>
            </button>
          {/each}
        </div>
      </div>
    </div>

    {#if active === 'A'}
      <VariantA {data} />
    {:else if active === 'B'}
      <VariantB {data} />
    {:else if active === 'C'}
      <VariantC {data} />
    {/if}
  </div>
</div>
