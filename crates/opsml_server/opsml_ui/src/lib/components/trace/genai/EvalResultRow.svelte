<script lang="ts">
  import type { GenAiEvalResult } from '$lib/components/scouter/genai/types';
  import { fmtPct, fmtInt } from '$lib/components/card/agent/observability/format';

  let { ev }: { ev: GenAiEvalResult } = $props();

  const scoreText = $derived(
    ev.score_value == null
      ? null
      : Math.abs(ev.score_value) <= 1
        ? fmtPct(ev.score_value)
        : fmtInt(ev.score_value),
  );
</script>

<div class="border-2 border-black bg-surface-50 p-2 flex flex-col gap-1">
  <div class="flex flex-wrap items-center gap-2">
    <span class="text-xs font-black uppercase tracking-wide text-primary-900">{ev.name}</span>
    {#if ev.score_label}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-200 text-primary-800">
        {ev.score_label}
      </span>
    {/if}
    {#if scoreText}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-primary-500 text-surface-50 font-mono">
        {scoreText}
      </span>
    {/if}
  </div>
  {#if ev.explanation}
    <p class="text-xs text-primary-800 whitespace-pre-wrap break-words">{ev.explanation}</p>
  {/if}
</div>
