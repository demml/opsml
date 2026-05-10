<script lang="ts">
  import type { GenAiSpanRecord } from '$lib/components/scouter/genai/types';

  let {
    span,
    toolDefinitions = null,
  }: {
    span: GenAiSpanRecord;
    toolDefinitions?: unknown;
  } = $props();

  const definitionsText = $derived(
    toolDefinitions ? JSON.stringify(toolDefinitions, null, 2) : null,
  );
</script>

<div class="border-2 border-black bg-surface-50 p-2">
  <div class="flex flex-wrap items-center gap-2 mb-2">
    {#if span.tool_name}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-200 text-primary-800">
        {span.tool_name}
      </span>
    {/if}
    {#if span.tool_type}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-100 text-primary-700">
        {span.tool_type}
      </span>
    {/if}
    {#if span.tool_call_id}
      <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black bg-surface-100 text-primary-700 font-mono">
        {span.tool_call_id}
      </span>
    {/if}
  </div>

  {#if definitionsText}
    <pre class="bg-surface-100 border-2 border-black p-2 text-xs font-mono whitespace-pre-wrap break-words text-primary-900">{definitionsText}</pre>
  {/if}
</div>
