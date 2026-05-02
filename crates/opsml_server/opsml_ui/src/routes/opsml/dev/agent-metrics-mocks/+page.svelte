<script lang="ts">
  import VariantA from '$lib/components/dev/agentMetricsMocks/VariantA_Classic.svelte';
  import VariantB from '$lib/components/dev/agentMetricsMocks/VariantB_CostFirst.svelte';
  import VariantC from '$lib/components/dev/agentMetricsMocks/VariantC_Compact.svelte';
  import { buildMockBundle } from '$lib/components/dev/agentMetricsMocks/mockData';

  type VariantKey = 'A' | 'B' | 'C';
  let active = $state<VariantKey>('A');

  const bundle = buildMockBundle({ seed: 42 });

  const tabs: { key: VariantKey; label: string; sub: string }[] = [
    { key: 'A', label: 'A · Classic', sub: 'Datadog/Grafana style' },
    { key: 'B', label: 'B · Cost-First', sub: 'Spend hero' },
    { key: 'C', label: 'C · Compact', sub: 'Dense grid' }
  ];
</script>

<div class="min-h-screen bg-surface-100 p-4">
  <div class="max-w-[1600px] mx-auto space-y-4">
    <!-- Page header + variant switcher -->
    <div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="text-[10px] font-black uppercase tracking-widest text-primary-600">DEV / SANDBOX</div>
          <h1 class="text-2xl font-black text-black uppercase tracking-tight">Agent Metrics Dashboard Mocks</h1>
          <p class="text-xs font-mono text-gray-700 mt-1">
            seed=42 · 60 buckets · 60s interval · service=research-agent
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
      <VariantA {bundle} />
    {:else if active === 'B'}
      <VariantB {bundle} />
    {:else if active === 'C'}
      <VariantC {bundle} />
    {/if}
  </div>
</div>
