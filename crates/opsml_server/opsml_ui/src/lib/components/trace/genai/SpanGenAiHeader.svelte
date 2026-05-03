<script lang="ts">
  import type { GenAiSpanRecord } from '$lib/components/scouter/genai/types';
  import { fmtCompact, fmtMs } from '$lib/components/card/agent/observability/format';

  let { span }: { span: GenAiSpanRecord } = $props();

  const modelLabel = $derived(
    span.response_model && span.request_model && span.response_model !== span.request_model
      ? `${span.request_model} → ${span.response_model}`
      : span.response_model || span.request_model || '—',
  );
</script>

<div class="flex flex-wrap items-center gap-2 border-2 border-black bg-surface-100 px-2 py-1.5">
  {#if span.provider_name}
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-primary-800">
      {span.provider_name}
    </span>
  {/if}
  <span class="text-xs font-mono font-black text-primary-900">{modelLabel}</span>

  {#if span.input_tokens != null || span.output_tokens != null}
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-primary-800">
      In {fmtCompact(span.input_tokens ?? 0)}
    </span>
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-primary-800">
      Out {fmtCompact(span.output_tokens ?? 0)}
    </span>
  {/if}

  {#if span.cache_read_input_tokens != null && span.cache_read_input_tokens > 0}
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-primary-700">
      Cache hit {fmtCompact(span.cache_read_input_tokens)}
    </span>
  {/if}

  <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-primary-800">
    {fmtMs(span.duration_ms)}
  </span>

  {#if span.finish_reasons.length > 0}
    {#each span.finish_reasons as reason, i (i)}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-warning-100 text-primary-900">
        {reason}
      </span>
    {/each}
  {/if}

  {#if span.error_type}
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-50 text-error-500">
      {span.error_type}
    </span>
  {/if}
</div>
