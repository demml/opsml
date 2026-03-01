<script lang="ts">
  import { Activity, AlertCircle, ChevronDown, ChevronUp, Copy, Check } from 'lucide-svelte';
  import { EXCEPTION_TRACEBACK, SPAN_ERROR, type SpanEvent } from './types';
  import { formatTimestamp } from './utils';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let { events }: { events: SpanEvent[] } = $props();

  function isErrorEvent(eventName: string): boolean {
    const name = eventName.toLowerCase();
    return name.includes('exception') || name.includes(SPAN_ERROR);
  }

  function getTraceback(attributes: Array<{ key: string; value: unknown }>): string | null {
    const attr = attributes.find(a => a.key === EXCEPTION_TRACEBACK);
    return attr ? String(attr.value) : null;
  }

  function getNonTracebackAttributes(attributes: Array<{ key: string; value: unknown }>) {
    return attributes.filter(a => a.key !== EXCEPTION_TRACEBACK);
  }

  function attrsToJson(attrs: Array<{ key: string; value: unknown }>): string {
    const obj: Record<string, unknown> = {};
    for (const a of attrs) obj[a.key] = a.value;
    return JSON.stringify(obj, null, 2);
  }

  // Collapsed state per event index — starts empty (all expanded)
  let collapsedEvents = $state<Set<number>>(new Set());
  let copiedIdx = $state<number | null>(null);

  function toggleEvent(idx: number) {
    const next = new Set(collapsedEvents);
    if (next.has(idx)) next.delete(idx); else next.add(idx);
    collapsedEvents = next;
  }

  function copyJson(json: string, idx: number) {
    navigator.clipboard.writeText(json);
    copiedIdx = idx;
    setTimeout(() => (copiedIdx = null), 2000);
  }
</script>

{#if events.length > 0}
  <div class="space-y-2">
    {#each events as event, idx}
      {@const isError = isErrorEvent(event.name)}
      {@const traceback = getTraceback(event.attributes)}
      {@const nonTracebackAttrs = getNonTracebackAttributes(event.attributes)}
      {@const isCollapsed = collapsedEvents.has(idx)}
      {@const json = nonTracebackAttrs.length > 0 ? attrsToJson(nonTracebackAttrs) : null}

      <div class="border-2 {isError ? 'border-error-600' : 'border-black'} rounded-base overflow-hidden shadow-small">

        <!-- Collapsible header -->
        <button
          onclick={() => toggleEvent(idx)}
          class="w-full flex items-center justify-between px-3 py-2 transition-colors duration-100
            {isError
              ? 'bg-error-100 hover:bg-error-200 border-b-2 border-error-600'
              : 'bg-primary-100 hover:bg-primary-200 border-b-2 border-black'}"
        >
          <div class="flex items-center gap-2 min-w-0">
            {#if isError}
              <AlertCircle class="w-3.5 h-3.5 text-error-600 flex-shrink-0" />
            {:else}
              <Activity class="w-3.5 h-3.5 text-primary-700 flex-shrink-0" />
            {/if}
            <span class="text-xs font-black uppercase tracking-wide truncate
              {isError ? 'text-error-900' : 'text-primary-900'}">{event.name}</span>
            {#if nonTracebackAttrs.length > 0}
              <span class="px-1.5 py-0.5 rounded-sm text-[10px] font-bold flex-shrink-0
                {isError
                  ? 'bg-error-200 border border-error-400 text-error-800'
                  : 'bg-primary-200 border border-primary-400 text-primary-800'}">
                {nonTracebackAttrs.length}
              </span>
            {/if}
            <span class="text-[10px] font-mono flex-shrink-0
              {isError ? 'text-error-600' : 'text-primary-400'}">
              {formatTimestamp(event.timestamp)}
            </span>
          </div>
          {#if isCollapsed}
            <ChevronDown class="w-3.5 h-3.5 flex-shrink-0 {isError ? 'text-error-600' : 'text-primary-600'}" />
          {:else}
            <ChevronUp class="w-3.5 h-3.5 flex-shrink-0 {isError ? 'text-error-600' : 'text-primary-600'}" />
          {/if}
        </button>

        <!-- Expanded body -->
        {#if !isCollapsed}
          <div class="bg-surface-50">

            <!-- Attributes as JSON codeblock (with copy button) -->
            {#if json}
              <div class="text-xs overflow-hidden relative">
                <button
                  class="absolute p-2 top-2 right-2 btn btn-sm bg-white border-2 border-black shadow-small z-20 hover:bg-slate-50 active:translate-y-[2px] active:shadow-none transition-all"
                  onclick={() => copyJson(json, idx)}
                  aria-label="Copy JSON"
                >
                  {#if copiedIdx === idx}
                    <Check class="w-4 h-4 text-secondary-600" />
                  {:else}
                    <Copy class="w-4 h-4" color="black" />
                  {/if}
                </button>
                <CodeBlock code={json} showLineNumbers={false} lang="json" prePadding="p-3" />
              </div>
            {/if}

            <!-- Exception traceback -->
            {#if traceback}
              <div class="p-3 {json ? 'border-t-2 border-error-600' : ''}">
                <div class="flex items-center gap-1.5 mb-2">
                  <AlertCircle class="w-3.5 h-3.5 text-error-600" />
                  <span class="text-xs font-black uppercase tracking-wide text-error-700">Exception Traceback</span>
                </div>
                <div class="max-h-64 overflow-y-auto border-2 border-error-600 rounded-base shadow-small text-xs overflow-hidden">
                  <CodeBlock code={traceback} showLineNumbers={false} lang="python" theme="traceback-theme" />
                </div>
              </div>
            {/if}

            <!-- Dropped attributes warning -->
            {#if event.dropped_attributes_count > 0}
              <div class="px-3 pb-2 text-xs text-warning-600 flex items-center gap-1 font-bold">
                <AlertCircle class="w-3 h-3" />
                {event.dropped_attributes_count} attributes dropped
              </div>
            {/if}

            <!-- Empty body state -->
            {#if !json && !traceback && event.dropped_attributes_count === 0}
              <p class="px-3 py-4 text-xs text-primary-400 italic text-center">No attributes recorded</p>
            {/if}

          </div>
        {/if}

      </div>
    {/each}
  </div>
{/if}
