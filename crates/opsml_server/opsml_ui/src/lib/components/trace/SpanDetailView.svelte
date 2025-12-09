<script lang="ts">
  import type { TraceSpan } from './types';
  import {
    formatTimestamp,
    formatDuration,
    formatAttributeValue,
    getServiceName,
    hasSpanError,
    getHttpStatusCode,
    parseSpanJson
  } from './utils';
  import { Info, Tags, Activity, Link2, AlertCircle, FileJson } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let {
    span,
    onSpanSelect,
    allSpans,
    slowestSpan
  }: {
    span: TraceSpan;
    onSpanSelect: (span: TraceSpan) => void;
    allSpans: TraceSpan[];
    slowestSpan?: TraceSpan | null;
  } = $props();

  const serviceName = $derived(getServiceName(span));
  const spanHasError = $derived(hasSpanError(span));
  const httpStatusCode = $derived(getHttpStatusCode(span));
  const parsedInput = $derived(parseSpanJson(span.input));
  const parsedOutput = $derived(parseSpanJson(span.output));

  // Create a lookup map for quick span access by ID
  const spanMap = $derived(
    new Map(allSpans.map(s => [s.span_id, s]))
  );

  function handlePathSegmentClick(spanId: string) {
    const targetSpan = spanMap.get(spanId);
    if (targetSpan) {
      onSpanSelect(targetSpan);
    }
  }

  function getStatusColor(statusCode: number): string {
    if (statusCode === 1) return 'bg-secondary-500'; // OK
    if (statusCode === 2) return 'bg-error-600'; // ERROR
    return 'bg-gray-400'; // UNSET
  }

  function getStatusLabel(statusCode: number): string {
    const labels: Record<number, string> = {
      0: 'UNSET',
      1: 'OK',
      2: 'ERROR',
    };
    return labels[statusCode] || 'UNKNOWN';
  }
</script>

<div class="flex flex-col h-full bg-white">
  <!-- Span Header -->
  <div class="p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class={`w-1 h-14 rounded ${spanHasError ? 'bg-error-600' : 'bg-secondary-500'}`}></div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-gray-900 truncate">{span.span_name}</h3>
        <p class="text-sm text-gray-600">{serviceName}</p>
        <p class="text-xs font-mono text-gray-500 mt-1">{span.span_id}</p>
      </div>
    </div>
  </div>

  <!-- Scrollable Content -->
  <div class="flex-1 overflow-auto p-4 space-y-4">

    <!-- Core Metrics -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Info color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Span Info</header>
      </div>

      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Duration" value={formatDuration(span.duration_ms)} textSize="text-xs"/>
        <Pill key="Status" value={getStatusLabel(span.status_code)} textSize="text-xs"/>
        {#if httpStatusCode}
          <Pill key="HTTP Status" value={String(httpStatusCode)} textSize="text-xs"/>
        {/if}
        <Pill key="Kind" value={span.span_kind || 'UNSPECIFIED'} textSize="text-xs"/>
        <Pill key="Depth" value={`Level ${span.depth}`} textSize="text-xs"/>
        <Pill key="Order" value={`#${span.span_order}`} textSize="text-xs"/>
        {#if slowestSpan && span.span_id === slowestSpan.span_id}
          <Pill key="Slowest" value="Yes" textSize="text-xs" bgColor="bg-retro-orange-100" textColor="text-retro-orange-900" borderColor="border-retro-orange-900" />
        {/if}
      </div>
    </section>

    <!-- Timing Information -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Start Time" value={span.start_time} textSize="text-xs"/>
        {#if span.end_time}
          <Pill key="End Time" value={span.end_time} textSize="text-xs"/>
        {/if}
        <Pill key="Duration" value={formatDuration(span.duration_ms)} textSize="text-xs"/>
      </div>
    </section>

    <!-- Span Path -->
     {#if span.path.length > 0}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Link2 color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Span Path</header>
        </div>

        <div class="flex flex-wrap gap-2">
          {#each span.path as pathSegment, i}
            <button
              class="px-2 py-1 bg-primary-100 border border-primary-800 rounded text-xs font-mono text-primary-900 hover:bg-primary-500 hover:text-white transition-colors cursor-pointer"
              onclick={() => handlePathSegmentClick(pathSegment)}
            >
              {pathSegment.slice(0, 7)}
            </button>
            {#if i < span.path.length - 1}
              <span class="text-gray-400 self-center">→</span>
            {/if}
          {/each}
        </div>
      </section>
    {/if}

    <!-- Input/Output -->
    {#if parsedInput}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <FileJson color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Input</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
          <CodeBlock
            code={JSON.stringify(parsedInput, null, 2)}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
          />
        </div>
      </section>
    {/if}

    {#if parsedOutput}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <FileJson color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Output</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
          <CodeBlock
            code={JSON.stringify(parsedOutput, null, 2)}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
          />
        </div>
      </section>
    {/if}

    <!-- Attributes -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Tags color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Attributes ({span.attributes.length})</header>
      </div>

      {#if span.attributes.length > 0}
        <div class="flex flex-col space-y-1 text-sm">
          {#each span.attributes as attr}
            <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs"/>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-gray-500 italic">No attributes</p>
      {/if}
    </section>

    <!-- Events -->
    {#if span.events.length > 0}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Activity color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Events ({span.events.length})</header>
        </div>

        <div class="space-y-3">
          {#each span.events as event}
            <div class="bg-surface-50 border-2 border-black rounded-base p-3 shadow-small">
              <div class="flex items-center gap-2 mb-2">
                {#if event.name.toLowerCase().includes('exception') || event.name.toLowerCase().includes('error')}
                  <AlertCircle class="text-error-600" size={16}/>
                {:else}
                  <Activity class="text-primary-500" size={16}/>
                {/if}
                <span class="text-sm font-bold text-gray-900">{event.name}</span>
              </div>

              <Pill key="Timestamp" value={formatTimestamp(event.timestamp)} textSize="text-xs"/>

              {#if event.attributes.length > 0}
                <div class="space-y-1 mt-2">
                  {#each event.attributes as attr}
                    <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs"/>
                  {/each}
                </div>
              {/if}

              {#if event.dropped_attributes_count > 0}
                <div class="text-xs text-warning-500 mt-2 flex items-center gap-1">
                  <AlertCircle size={12}/>
                  {event.dropped_attributes_count} attributes dropped
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Links -->
    {#if span.links.length > 0}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Link2 color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Links ({span.links.length})</header>
        </div>

        <div class="space-y-3">
          {#each span.links as link}
            <div class="bg-surface-50 border-2 border-black rounded-base p-3 shadow-small">
              <div class="flex flex-col space-y-1">
                <Pill key="Trace ID" value={link.trace_id} textSize="text-xs"/>
                <Pill key="Span ID" value={link.span_id} textSize="text-xs"/>
                {#if link.trace_state}
                  <Pill key="State" value={link.trace_state} textSize="text-xs"/>
                {/if}
              </div>

              {#if link.dropped_attributes_count > 0}
                <div class="text-xs text-warning-500 mt-2 flex items-center gap-1">
                  <AlertCircle size={12}/>
                  {link.dropped_attributes_count} attributes dropped
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Error Details -->
    {#if spanHasError && span.status_message}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-error-600">
          <AlertCircle color="#d93025"/>
          <header class="pl-2 text-error-600 text-sm font-bold">Error Details</header>
        </div>

        <div class="bg-surface-50 border-2 border-error-600 rounded-base p-3 shadow-small">
          <p class="text-sm text-error-600">{span.status_message}</p>
        </div>
      </section>
    {/if}

  </div>
</div>