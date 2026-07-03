<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw } from 'lucide-svelte';
  import { getServerGenAiTraceMetrics, formatDuration } from '$lib/components/trace/utils';
  import type {
    GenAiTraceMetricsResponse,
    GenAiSpanRecord,
  } from '$lib/components/scouter/genai/types';

  export let traceId: string;

  let loading = false;
  let error: string | null = null;
  let genai: GenAiTraceMetricsResponse | null = null;

  const fetchMetrics = async () => {
    loading = true;
    error = null;
    try {
      genai = await getServerGenAiTraceMetrics(window.fetch, traceId);
    } catch (e: any) {
      error = e?.message ?? String(e);
      genai = null;
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    if (traceId) fetchMetrics();
  });

  function displayCost(span: GenAiSpanRecord): string {
    // Some backends may attach a cost field; prefer explicit value if present
    // The GenAiSpanRecord doesn't include cost in the canonical schema, so be defensive.
    // @ts-ignore
    const c = (span as any).cost ?? (span as any).total_cost ?? null;
    return c != null ? `$${Number(c).toFixed(4)}` : 'N/A';
  }
</script>

<div class="p-4 bg-surface-50 h-full">
  <div class="flex items-center justify-between mb-3">
    <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">GenAI Span Metrics</h3>
    <div class="flex items-center gap-2">
      <button
        class="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-black uppercase border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small hover:bg-primary-100"
        on:click={fetchMetrics}
        aria-label="Refresh GenAI metrics"
      >
        <RefreshCw class="w-4 h-4" />
        Refresh
      </button>
    </div>
  </div>

  {#if loading}
    <div class="space-y-2">
      <div class="h-10 rounded-base bg-primary-100 animate-pulse"></div>
      <div class="h-8 rounded-base bg-primary-100 animate-pulse"></div>
      <div class="h-8 rounded-base bg-primary-100 animate-pulse"></div>
    </div>
  {:else if error}
    <div class="p-3 border-2 border-black bg-error-100 text-error-800 rounded-base">
      <strong class="font-bold">Failed to load GenAI metrics:</strong>
      <div class="mt-1 text-sm">{error}</div>
    </div>
  {:else if genai && genai.has_genai_spans}
    <div class="overflow-auto">
      <table class="w-full border-collapse text-sm">
        <thead>
          <tr class="border-b-2 border-black">
            <th class="text-left px-3 py-2 font-mono text-xs">Span ID</th>
            <th class="text-left px-3 py-2 font-mono text-xs">Operation</th>
            <th class="text-left px-3 py-2 font-mono text-xs">Model</th>
            <th class="text-right px-3 py-2 font-mono text-xs">Input Tokens</th>
            <th class="text-right px-3 py-2 font-mono text-xs">Output Tokens</th>
            <th class="text-right px-3 py-2 font-mono text-xs">Latency</th>
            <th class="text-right px-3 py-2 font-mono text-xs">Cost</th>
          </tr>
        </thead>
        <tbody>
          {#each genai.spans as s}
            <tr class="odd:bg-surface-50 even:bg-primary-100/50">
              <td class="px-3 py-2 font-mono truncate max-w-[220px]">{s.span_id}</td>
              <td class="px-3 py-2">{s.operation_name ?? '-'}</td>
              <td class="px-3 py-2">{s.request_model ?? s.response_model ?? '-'}</td>
              <td class="px-3 py-2 text-right">{s.input_tokens ?? '-'}</td>
              <td class="px-3 py-2 text-right">{s.output_tokens ?? '-'}</td>
              <td class="px-3 py-2 text-right">{formatDuration(s.duration_ms)}</td>
              <td class="px-3 py-2 text-right">{displayCost(s)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {:else}
    <div class="p-4 border-2 border-black bg-surface-50 rounded-base">
      <div class="text-sm text-primary-700">No GenAI spans found for this trace.</div>
    </div>
  {/if}
</div>

<style>
  /* Minimal component-local styles to blend with OpsML theme */
  table th, table td {
    border-bottom: 0;
  }

  .animate-pulse {
    animation: pulse 1.2s ease-in-out infinite;
  }

  @keyframes pulse {
    0% { opacity: 1 }
    50% { opacity: 0.4 }
    100% { opacity: 1 }
  }
</style>
