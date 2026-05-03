<script lang="ts">
  import type { GenAiSpanRecord } from '$lib/components/scouter/genai/types';
  import SpanGenAiHeader from './SpanGenAiHeader.svelte';
  import MessageList from './MessageList.svelte';
  import ToolCallBlock from './ToolCallBlock.svelte';
  import EvalResultRow from './EvalResultRow.svelte';
  import { parseMessages, safeParseJson } from './messageFormat';

  let { span }: { span: GenAiSpanRecord } = $props();

  const inputMessages = $derived(parseMessages(span.input_messages));
  const outputMessages = $derived(parseMessages(span.output_messages));
  const systemInstructions = $derived((() => {
    const raw = span.system_instructions;
    if (!raw) return null;
    const parsed = safeParseJson<unknown>(raw);
    if (typeof parsed === "string") return parsed;
    if (parsed != null) return JSON.stringify(parsed, null, 2);
    return raw;
  })());
  const toolDefinitions = $derived(safeParseJson(span.tool_definitions));
</script>

<div class="flex flex-col gap-3 p-3">
  <SpanGenAiHeader {span} />

  {#if systemInstructions}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">System</h3>
      <pre class="bg-surface-100 border-2 border-black p-2 text-xs font-mono whitespace-pre-wrap break-words text-primary-900">{systemInstructions}</pre>
    </section>
  {/if}

  {#if inputMessages}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Input</h3>
      <MessageList messages={inputMessages} />
    </section>
  {:else if span.input_messages}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Input</h3>
      <pre class="bg-surface-100 border-2 border-black p-2 text-xs font-mono whitespace-pre-wrap break-words text-primary-900">{span.input_messages}</pre>
    </section>
  {/if}

  {#if outputMessages}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Output</h3>
      <MessageList messages={outputMessages} />
    </section>
  {:else if span.output_messages}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Output</h3>
      <pre class="bg-surface-100 border-2 border-black p-2 text-xs font-mono whitespace-pre-wrap break-words text-primary-900">{span.output_messages}</pre>
    </section>
  {/if}

  {#if span.tool_name || toolDefinitions}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Tool</h3>
      <ToolCallBlock {span} {toolDefinitions} />
    </section>
  {/if}

  {#if span.eval_results.length > 0}
    <section class="flex flex-col gap-2">
      <h3 class="text-sm font-black uppercase tracking-wide text-primary-800">Evals</h3>
      <div class="flex flex-col gap-2">
        {#each span.eval_results as ev, i (i)}
          <!-- index-keyed: list is render-once; revisit if eval contracts carry stable IDs -->
          <EvalResultRow {ev} />
        {/each}
      </div>
    </section>
  {/if}
</div>
