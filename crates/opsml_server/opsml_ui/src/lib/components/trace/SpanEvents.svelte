<script lang="ts">
  import { Activity, AlertCircle } from 'lucide-svelte';
  import { EXCEPTION_TRACEBACK, SPAN_ERROR, type SpanEvent } from './types';
  import { formatTimestamp, formatAttributeValue } from './utils';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  /**
   * Component for displaying span events, including exception tracebacks
   */
  let { events }: { events: SpanEvent[] } = $props();

  /**
   * Check if an event represents an error/exception
   */
  function isErrorEvent(eventName: string): boolean {
    const name = eventName.toLowerCase();
    return name.includes('exception') || name.includes(SPAN_ERROR);
  }

  /**
   * Extract traceback attribute from event attributes
   */
  function getTraceback(attributes: Array<{ key: string; value: unknown }>): string | null {
    const tracebackAttr = attributes.find(attr => attr.key === EXCEPTION_TRACEBACK);
    return tracebackAttr ? String(tracebackAttr.value) : null;
  }

  /**
   * Filter out traceback attributes for pill display
   */
  function getNonTracebackAttributes(attributes: Array<{ key: string; value: unknown }>) {
    return attributes.filter(attr => attr.key !== EXCEPTION_TRACEBACK);
  }
</script>

{#if events.length > 0}
  <section>
    <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
      <Activity color="#8059b6" />
      <header class="pl-2 text-primary-950 text-sm font-bold">Events ({events.length})</header>
    </div>

    <div class="space-y-3">
      {#each events as event}
        {@const isError = isErrorEvent(event.name)}
        {@const traceback = getTraceback(event.attributes)}
        {@const nonTracebackAttrs = getNonTracebackAttributes(event.attributes)}

        <div class="bg-surface-50 border-2 border-black rounded-base p-2 shadow-small">
          <!-- Event Header -->
          <div class="flex items-center gap-2 mb-2">
            {#if isError}
              <AlertCircle class="text-error-600" size={16} />
            {:else}
              <Activity class="text-primary-500" size={16} />
            {/if}
            <span class="text-sm font-bold text-gray-900">{event.name}</span>
          </div>

          <!-- Timestamp -->
          <div class="mb-1 text-sm">
            <Pill key="Timestamp" value={formatTimestamp(event.timestamp)} textSize="text-xs" />
          </div>

          <!-- Non-Traceback Attributes -->
          {#if nonTracebackAttrs.length > 0}
            <div class="flex flex-col space-y-1 text-sm">
              {#each nonTracebackAttrs as attr}
                <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs" />
              {/each}
            </div>
          {/if}

          <!-- Traceback (if present) -->
          {#if traceback}
            <div class="mt-3">
              <!-- Traceback Header -->
              <div class="flex items-center gap-1 mb-1">
                <AlertCircle class="text-error-600" size={14} />
                <span class="text-xs font-bold text-error-600">Exception Traceback</span>
              </div>
              
              <!-- Traceback Code Block -->
              <div class="max-h-64 overflow-y-auto bg-surface-100 rounded-base border-2 border-error-600 p-1 shadow-small text-xs">
                <CodeBlock
                  code={traceback}
                  showLineNumbers={false}
                  lang="python"
                  theme="traceback-theme"
                  prePadding="p-1"
                />
              </div>
            </div>
          {/if}

          <!-- Dropped Attributes Warning -->
          {#if event.dropped_attributes_count > 0}
            <div class="text-xs text-warning-500 mt-2 flex items-center gap-1">
              <AlertCircle size={12} />
              {event.dropped_attributes_count} attributes dropped
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </section>
{/if}