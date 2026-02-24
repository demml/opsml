<script lang="ts">
  import { type TraceSpan } from './types';
  import {
    formatDuration,
    formatAttributeValue,
    hasSpanError,
    getHttpStatusCode,
    parseSpanJson
  } from './utils';
  import { Info, Tags, Activity, Link2, AlertCircle, FileJson, ChevronDown, ChevronUp, Copy, Check } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import SpanEvents from './SpanEvents.svelte';

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

  const serviceName = $derived(span.service_name);
  const spanHasError = $derived(hasSpanError(span));
  const httpStatusCode = $derived(getHttpStatusCode(span));
  const parsedInput = $derived(parseSpanJson(span.input));
  const parsedOutput = $derived(parseSpanJson(span.output));

  const spanMap = $derived(new Map(allSpans.map(s => [s.span_id, s])));

  let showInput = $state(true);
  let showOutput = $state(true);
  let copiedSpanId = $state(false);

  function handlePathSegmentClick(spanId: string) {
    const targetSpan = spanMap.get(spanId);
    if (targetSpan) {
      onSpanSelect(targetSpan);
    }
  }

  function copySpanId() {
    navigator.clipboard.writeText(span.span_id);
    copiedSpanId = true;
    setTimeout(() => copiedSpanId = false, 2000);
  }

  function getStatusLabel(statusCode: number): string {
    const labels: Record<number, string> = { 0: 'UNSET', 1: 'OK', 2: 'ERROR' };
    return labels[statusCode] || 'UNKNOWN';
  }

  const headerBg = $derived(
    spanHasError ? 'bg-error-100 border-b-error-600' :
    span.status_code === 1 ? 'bg-secondary-100' :
    'bg-surface-100'
  );

  const statusPillClasses = $derived(
    spanHasError ? 'bg-error-600 text-white border-error-800' :
    span.status_code === 1 ? 'bg-secondary-500 text-black border-secondary-800' :
    'bg-gray-300 text-black border-gray-500'
  );

  const accentBarColor = $derived(spanHasError ? 'bg-error-600' : span.status_code === 1 ? 'bg-secondary-500' : 'bg-gray-400');

  const isSlowest = $derived(slowestSpan && span.span_id === slowestSpan.span_id);
</script>

<div class="flex flex-col h-full bg-white overflow-hidden">

  <!-- Bold neo-brutalist span header -->
  <div class="flex-shrink-0 border-b-2 border-black {headerBg}">
    <div class="flex gap-0">
      <!-- Status accent bar -->
      <div class="w-2 flex-shrink-0 {accentBarColor}"></div>

      <div class="flex-1 p-3 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0 flex-1">
            <h3 class="font-black text-black text-sm leading-tight truncate">{span.span_name}</h3>
            <p class="text-xs text-gray-600 mt-0.5 truncate">{serviceName}</p>
          </div>
          <!-- Status + copy -->
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <span class="px-2 py-0.5 text-xs font-black border-2 rounded uppercase {statusPillClasses}">
              {getStatusLabel(span.status_code)}
            </span>
            {#if isSlowest}
              <span class="px-2 py-0.5 text-xs font-black border-2 rounded uppercase warn-color">
                Slowest
              </span>
            {/if}
          </div>
        </div>

        <!-- Span ID row with copy -->
        <div class="flex items-center gap-1.5 mt-2">
          <code class="text-xs font-mono text-gray-500 truncate flex-1">{span.span_id}</code>
          <button
            onclick={copySpanId}
            class="flex-shrink-0 p-1 rounded border border-black/30 bg-white/60 hover:bg-white transition-colors"
            aria-label="Copy span ID"
          >
            {#if copiedSpanId}
              <Check class="w-3 h-3 text-secondary-600" />
            {:else}
              <Copy class="w-3 h-3 text-gray-500" />
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Scrollable detail sections -->
  <div class="flex-1 overflow-y-auto">

    <!-- Error banner (if applicable) -->
    {#if spanHasError && span.status_message}
      <div class="mx-3 mt-3 flex items-start gap-2 p-3 bg-error-100 border-2 border-error-600 shadow-small">
        <AlertCircle class="w-4 h-4 text-error-600 flex-shrink-0 mt-0.5" />
        <div>
          <p class="text-xs font-black text-error-700 uppercase tracking-wide mb-0.5">Error</p>
          <p class="text-xs text-error-700 font-mono">{span.status_message}</p>
        </div>
      </div>
    {/if}

    <div class="p-3 space-y-4">

      <!-- Span Info -->
      <section>
        <div class="flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black">
          <Info class="w-3.5 h-3.5" color="#8059b6" />
          <span class="text-xs font-black uppercase tracking-wide text-primary-950">Span Info</span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          <Pill key="Duration" value={formatDuration(span.duration_ms)} textSize="text-xs"/>
          <Pill key="Status" value={getStatusLabel(span.status_code)} textSize="text-xs"/>
          {#if httpStatusCode}
            <Pill key="HTTP" value={String(httpStatusCode)} textSize="text-xs"/>
          {/if}
          <Pill key="Kind" value={span.span_kind || 'UNSPECIFIED'} textSize="text-xs"/>
          <Pill key="Depth" value={`L${span.depth}`} textSize="text-xs"/>
          <Pill key="Order" value={`#${span.span_order}`} textSize="text-xs"/>
          {#if isSlowest}
            <Pill key="Slowest" value="Yes" textSize="text-xs" bgColor="bg-retro-orange-100" textColor="text-retro-orange-900" borderColor="border-retro-orange-900" />
          {/if}
        </div>
      </section>

      <!-- Timing -->
      <section>
        <div class="flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black">
          <Activity class="w-3.5 h-3.5" color="#8059b6" />
          <span class="text-xs font-black uppercase tracking-wide text-primary-950">Timing</span>
        </div>
        <div class="flex flex-col gap-1">
          <Pill key="Start" value={span.start_time} textSize="text-xs"/>
          {#if span.end_time}
            <Pill key="End" value={span.end_time} textSize="text-xs"/>
          {/if}
          <Pill key="Duration" value={formatDuration(span.duration_ms)} textSize="text-xs"/>
        </div>
      </section>

      <!-- Span Path -->
      {#if span.path.length > 0}
        <section>
          <div class="flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black">
            <Link2 class="w-3.5 h-3.5" color="#8059b6" />
            <span class="text-xs font-black uppercase tracking-wide text-primary-950">Path</span>
            <span class="ml-auto text-xs font-mono text-gray-500">{span.path.length} hops</span>
          </div>
          <div class="flex flex-wrap gap-1.5 items-center">
            {#each span.path as pathSegment, i}
              <button
                class="px-2 py-1 bg-primary-100 border-1 border-primary-700 shadow-small text-xs font-mono text-primary-950 shadow-small shadow-hover-small transition-all cursor-pointer"
                onclick={() => handlePathSegmentClick(pathSegment)}
                title={pathSegment}
              >
                {pathSegment.slice(0, 8)}
              </button>
              {#if i < span.path.length - 1}
                <span class="text-gray-400 text-xs font-bold">→</span>
              {/if}
            {/each}
          </div>
        </section>
      {/if}

      <!-- Input (collapsible) -->
      {#if parsedInput}
        {#key span.span_id}
          <section>
            <button
              class="w-full flex items-center gap-2 py-1 mb-2 border-1 border-primary-500 px-1 rounded-sm cursor-pointer transition-opacity hover:bg-slate-100 text-primary-800 hover:text-primary-800"
              onclick={() => showInput = !showInput}
            >
              <FileJson class="w-3.5 h-3.5 text-primary-700" />
              <span class="text-xs font-black uppercase tracking-wide text-primary-950">Input</span>
              <span class="ml-auto">
                {#if showInput}<ChevronUp class="w-3.5 h-3.5 text-gray-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-gray-500"/>{/if}
              </span>
            </button>
            {#if showInput}
              <div class="bg-surface-50 rounded-base border-1 border-black shadow-small text-xs overflow-hidden">
                <CodeBlock
                  code={JSON.stringify(parsedInput, null, 2)}
                  showLineNumbers={false}
                  lang="json"
                  prePadding="p-2"
                />
              </div>
            {/if}
          </section>
        {/key}
      {/if}

      <!-- Output (collapsible) -->
      {#if parsedOutput}
        {#key span.span_id}
          <section>
            <button
              class="w-full flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black hover:bg-surface-100 -mx-1 px-1 rounded-sm transition-colors"
              onclick={() => showOutput = !showOutput}
            >
              <FileJson class="w-3.5 h-3.5 text-primary-700" />
              <span class="text-xs font-black uppercase tracking-wide text-primary-950">Output</span>
              <span class="ml-auto">
                {#if showOutput}<ChevronUp class="w-3.5 h-3.5 text-gray-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-gray-500"/>{/if}
              </span>
            </button>
            {#if showOutput}
              <div class="bg-surface-50 rounded-base border-2 border-black shadow-small text-xs overflow-hidden">
                <CodeBlock
                  code={JSON.stringify(parsedOutput, null, 2)}
                  showLineNumbers={false}
                  lang="json"
                  prePadding="p-2"
                />
              </div>
            {/if}
          </section>
        {/key}
      {/if}

      <!-- Attributes -->
      <section>
        <div class="flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black">
          <Tags class="w-3.5 h-3.5" color="#8059b6" />
          <span class="text-xs font-black uppercase tracking-wide text-primary-950">Attributes</span>
          <span class="ml-auto px-1.5 py-0.5 text-xs font-bold bg-primary-100 border border-primary-700 rounded text-primary-800">
            {span.attributes.length}
          </span>
        </div>
        {#if span.attributes.length > 0}
          <div class="flex flex-col gap-1">
            {#each span.attributes as attr}
              <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs"/>
            {/each}
          </div>
        {:else}
          <p class="text-xs text-gray-400 italic">No attributes recorded</p>
        {/if}
      </section>

      <!-- Events -->
      <SpanEvents events={span.events} />

      <!-- Links -->
      {#if span.links.length > 0}
        <section>
          <div class="flex items-center gap-2 pb-1.5 mb-2 border-b-2 border-black">
            <Link2 class="w-3.5 h-3.5" color="#8059b6" />
            <span class="text-xs font-black uppercase tracking-wide text-primary-950">Links</span>
            <span class="ml-auto px-1.5 py-0.5 text-xs font-bold bg-primary-100 border border-primary-700 rounded text-primary-800">
              {span.links.length}
            </span>
          </div>
          <div class="space-y-2">
            {#each span.links as link}
              <div class="bg-surface-50 border-2 border-black rounded-base p-2.5 shadow-small">
                <div class="flex flex-col gap-1">
                  <Pill key="Trace ID" value={link.trace_id} textSize="text-xs"/>
                  <Pill key="Span ID" value={link.span_id} textSize="text-xs"/>
                  {#if link.trace_state}
                    <Pill key="State" value={link.trace_state} textSize="text-xs"/>
                  {/if}
                </div>
                {#if link.dropped_attributes_count > 0}
                  <div class="text-xs text-warning-600 mt-2 flex items-center gap-1 font-bold">
                    <AlertCircle class="w-3 h-3" />
                    {link.dropped_attributes_count} attributes dropped
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </section>
      {/if}

    </div>
  </div>
</div>