<script lang="ts">
  import { type TraceSpan } from './types';
  import {
    formatDuration,
    formatAttributeValue,
    hasSpanError,
    getHttpStatusCode,
    parseSpanJson
  } from './utils';
  import {
    Info, Tags, Activity, Link2, AlertCircle, FileJson,
    ChevronDown, ChevronUp, Copy, Check, Search
  } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import SpanEvents from './SpanEvents.svelte';
  import { EXCEPTION_TRACEBACK } from './types';

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

  // ─── Derived values ────────────────────────────────────────────────────────

  const spanHasError = $derived(hasSpanError(span));
  const httpStatusCode = $derived(getHttpStatusCode(span));
  const parsedInput = $derived(parseSpanJson(span.input));
  const parsedOutput = $derived(parseSpanJson(span.output));
  const spanMap = $derived(new Map(allSpans.map(s => [s.span_id, s])));
  const isSlowest = $derived(slowestSpan && span.span_id === slowestSpan.span_id);

  // LLM-specific attributes
  const tokenAttrs = $derived((() => {
    const map: Record<string, string> = {};
    for (const attr of span.attributes) {
      if (attr.key.includes('token') || attr.key.includes('usage')) {
        map[attr.key] = String(attr.value);
      }
    }
    return map;
  })());

  const modelAttr = $derived(span.attributes.find(a => a.key.includes('model'))?.value);

  // Error details from events
  const errorEvents = $derived(span.events.filter(e => {
    const n = e.name.toLowerCase();
    return n.includes('exception') || n.includes('error');
  }));

  const errorCount = $derived(spanHasError ? Math.max(1, errorEvents.length) : 0);

  // Attributes search
  let attrSearch = $state('');
  const filteredAttributes = $derived(
    attrSearch.trim()
      ? span.attributes.filter(a =>
          a.key.toLowerCase().includes(attrSearch.toLowerCase()) ||
          String(a.value).toLowerCase().includes(attrSearch.toLowerCase())
        )
      : span.attributes
  );

  // ─── Tab state ─────────────────────────────────────────────────────────────

  type Tab = 'overview' | 'errors' | 'attributes' | 'events';
  let activeTab = $state<Tab>('overview');

  // ─── UI helpers ────────────────────────────────────────────────────────────

  let showInput = $state(true);
  let showOutput = $state(true);
  let copiedSpanId = $state(false);

  function getStatusLabel(code: number): string {
    return ({ 0: 'UNSET', 1: 'OK', 2: 'ERROR' } as Record<number, string>)[code] || 'UNKNOWN';
  }

  const statusBadgeClasses = $derived(
    spanHasError ? 'bg-error-100 text-error-800 border-error-600' :
    span.status_code === 1 ? 'bg-secondary-100 text-secondary-800 border-secondary-600' :
    'bg-gray-100 text-gray-700 border-gray-400'
  );

  function copySpanId() {
    navigator.clipboard.writeText(span.span_id);
    copiedSpanId = true;
    setTimeout(() => copiedSpanId = false, 2000);
  }

  function handlePathSegmentClick(spanId: string) {
    const target = spanMap.get(spanId);
    if (target) onSpanSelect(target);
  }

  function getTraceback(attributes: Array<{ key: string; value: unknown }>): string | null {
    const attr = attributes.find(a => a.key === EXCEPTION_TRACEBACK);
    return attr ? String(attr.value) : null;
  }

  function getNonTracebackAttributes(attributes: Array<{ key: string; value: unknown }>) {
    return attributes.filter(a => a.key !== EXCEPTION_TRACEBACK);
  }

</script>

<div class="flex flex-col h-full bg-white overflow-hidden">

  <!-- ─── Sub-tab bar ─────────────────────────────────────────────────────── -->
  <div class="flex-shrink-0 flex items-center gap-0 border-b-2 border-black bg-surface-50 px-3 pt-2 overflow-x-auto">
    <!-- Overview -->
    <button
      onclick={() => activeTab = 'overview'}
      class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-xs font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
        {activeTab === 'overview' ? 'border-primary-600 text-primary-800' : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'}"
    >
      <Info class="w-3 h-3" />
      Overview
    </button>

    <!-- Errors -->
    <button
      onclick={() => activeTab = 'errors'}
      class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-xs font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
        {activeTab === 'errors' ? 'border-primary-600 text-primary-800' : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'}"
    >
      <AlertCircle class="w-3 h-3" />
      Errors
      {#if errorCount > 0}
        <span class="px-1.5 py-0.5 rounded-base text-[10px] font-black bg-error-100 text-error-800 border border-error-400">{errorCount}</span>
      {/if}
    </button>

    <!-- Attributes -->
    <button
      onclick={() => activeTab = 'attributes'}
      class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-xs font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
        {activeTab === 'attributes' ? 'border-primary-600 text-primary-800' : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'}"
    >
      <Tags class="w-3 h-3" />
      Attributes
      {#if span.attributes.length > 0}
        <span class="px-1.5 py-0.5 rounded-base text-[10px] font-black bg-primary-100 text-primary-800 border border-primary-300">{span.attributes.length}</span>
      {/if}
    </button>

    <!-- Events -->
    <button
      onclick={() => activeTab = 'events'}
      class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-xs font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
        {activeTab === 'events' ? 'border-primary-600 text-primary-800' : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'}"
    >
      <Activity class="w-3 h-3" />
      Events
      {#if span.events.length > 0}
        <span class="px-1.5 py-0.5 rounded-base text-[10px] font-black bg-primary-100 text-primary-800 border border-primary-300">{span.events.length}</span>
      {/if}
    </button>
  </div>

  <!-- ─── Tab panels ──────────────────────────────────────────────────────── -->
  <div class="flex-1 overflow-y-auto">

    <!-- OVERVIEW TAB -->
    {#if activeTab === 'overview'}
      <div class="flex flex-col lg:flex-row gap-0 h-full divide-y-2 lg:divide-y-0 lg:divide-x-2 divide-black">

        <!-- Left: core span metadata -->
        <div class="flex-1 min-w-0 p-4 space-y-3 overflow-y-auto">
          <!-- Span name + status row -->
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <h3 class="text-sm font-black text-black leading-tight truncate">{span.span_name}</h3>
              <p class="text-xs text-gray-500 font-mono mt-0.5 truncate">{span.service_name}</p>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <span class="px-2 py-0.5 text-xs font-black border-2 uppercase rounded-base {statusBadgeClasses}">
                {getStatusLabel(span.status_code)}
              </span>
              {#if isSlowest}
                <span class="px-2 py-0.5 text-xs font-black border-2 rounded-base warn-color uppercase">Slowest</span>
              {/if}
            </div>
          </div>

          <!-- Error banner -->
          {#if spanHasError && span.status_message}
            <div class="flex items-start gap-2 p-2.5 bg-error-50 border-2 border-error-500 rounded-base shadow-small">
              <AlertCircle class="w-4 h-4 text-error-600 flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-xs font-black text-error-700 uppercase tracking-wide mb-0.5">Error</p>
                <p class="text-xs text-error-700 font-mono">{span.status_message}</p>
              </div>
            </div>
          {/if}

          <!-- Key-value metadata table -->
          <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
            <table class="w-full text-xs overflow-hidden">
              <tbody>
                {#each [
                  ['Trace ID',   span.trace_id],
                  ['Span ID',    span.span_id],
                  ['Parent ID',  span.parent_span_id || '—'],
                  ['Start',      span.start_time],
                  ['End',        span.end_time || '—'],
                  ['Duration',   formatDuration(span.duration_ms)],
                  ['Kind',       span.span_kind || 'UNSPECIFIED'],
                  ['Depth',      `L${span.depth}`],
                  ...(httpStatusCode ? [['HTTP', String(httpStatusCode)]] : []),
                ] as row, i}
                  <tr class="{i % 2 === 0 ? 'bg-white' : 'bg-surface-400'}">
                    <td class="px-2.5 py-1.5 font-black text-primary-800 uppercase tracking-wide border-b border-black/10 w-28 flex-shrink-0 whitespace-nowrap">{row[0]}</td>
                    <td class="px-2.5 py-1.5 font-mono text-black border-b border-black/10 break-all">
                      {#if row[0] === 'Span ID'}
                        <div class="flex items-center gap-1.5">
                          <span class="truncate">{span.span_id}</span>
                          <button
                            onclick={copySpanId}
                            class="flex-shrink-0 p-0.5 rounded border border-black/20 bg-white hover:bg-surface-100 transition-colors"
                            aria-label="Copy span ID"
                          >
                            {#if copiedSpanId}
                              <Check class="w-3 h-3 text-secondary-600" />
                            {:else}
                              <Copy class="w-3 h-3 text-gray-400" />
                            {/if}
                          </button>
                        </div>
                      {:else}
                        {row[1]}
                      {/if}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          <!-- Span path -->
          {#if span.path.length > 0}
            <div>
              <div class="flex items-center gap-1.5 mb-1.5">
                <Link2 class="w-3.5 h-3.5 text-primary-700" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-950">Path</span>
                <span class="ml-auto text-xs font-mono text-gray-500">{span.path.length} hops</span>
              </div>
              <div class="flex flex-wrap gap-1.5 items-center">
                {#each span.path as seg, i}
                  <button
                    class="px-2 py-0.5 bg-primary-100 border border-primary-600 text-xs font-mono text-primary-900 shadow-small shadow-hover-small transition-all rounded-sm"
                    onclick={() => handlePathSegmentClick(seg)}
                    title={seg}
                  >{seg.slice(0, 8)}</button>
                  {#if i < span.path.length - 1}
                    <span class="text-gray-400 text-xs">→</span>
                  {/if}
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- Right: LLM / IO data -->
        <div class="flex-1 min-w-0 p-4 space-y-3 overflow-y-auto bg-surface-50">

          <!-- Model + tokens (if present) -->
          {#if modelAttr || Object.keys(tokenAttrs).length > 0}
            <div class="space-y-2">
              <h4 class="text-xs font-black uppercase tracking-wide text-primary-950 border-b-2 border-black pb-1">LLM Details</h4>
              {#if modelAttr}
                <div class="flex items-center gap-2 p-2 bg-white border-2 border-black rounded-base shadow-small">
                  <span class="text-xs font-bold text-gray-500 w-14 flex-shrink-0">Model</span>
                  <span class="text-xs font-mono text-black font-bold">{modelAttr}</span>
                </div>
              {/if}
              {#if Object.keys(tokenAttrs).length > 0}
                <div class="grid grid-cols-3 gap-1.5">
                  {#each Object.entries(tokenAttrs) as [key, val]}
                    <div class="p-2 bg-white border-2 border-black rounded-base shadow-small text-center">
                      <div class="text-xs font-mono font-black text-primary-800">{val}</div>
                      <div class="text-[10px] font-bold text-gray-500 uppercase tracking-wide mt-0.5 truncate">{key.split('.').pop()}</div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}

          <!-- Input (collapsible) -->
          {#if parsedInput}
            {#key span.span_id}
              <div>
                <button
                  class="w-full flex items-center gap-2 px-2 py-1.5 mb-1.5 border-2 border-primary-400 bg-white rounded-sm cursor-pointer hover:bg-surface-100 transition-colors text-primary-800"
                  onclick={() => showInput = !showInput}
                >
                  <FileJson class="w-3.5 h-3.5 text-primary-700" />
                  <span class="text-xs font-black uppercase tracking-wide">Input</span>
                  <span class="ml-auto">
                    {#if showInput}<ChevronUp class="w-3.5 h-3.5 text-gray-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-gray-500"/>{/if}
                  </span>
                </button>
                {#if showInput}
                  <div class="bg-white rounded-base border-2 border-black shadow-small text-xs overflow-hidden">
                    <CodeBlock code={JSON.stringify(parsedInput, null, 2)} showLineNumbers={false} lang="json" prePadding="p-2" />
                  </div>
                {/if}
              </div>
            {/key}
          {/if}

          <!-- Output (collapsible) -->
          {#if parsedOutput}
            {#key span.span_id}
              <div>
                <button
                  class="w-full flex items-center gap-2 px-2 py-1.5 mb-1.5 border-2 border-primary-400 bg-white rounded-sm cursor-pointer hover:bg-surface-100 transition-colors text-primary-800"
                  onclick={() => showOutput = !showOutput}
                >
                  <FileJson class="w-3.5 h-3.5 text-primary-700" />
                  <span class="text-xs font-black uppercase tracking-wide">Output</span>
                  <span class="ml-auto">
                    {#if showOutput}<ChevronUp class="w-3.5 h-3.5 text-gray-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-gray-500"/>{/if}
                  </span>
                </button>
                {#if showOutput}
                  <div class="bg-white rounded-base border-2 border-black shadow-small text-xs overflow-hidden">
                    <CodeBlock code={JSON.stringify(parsedOutput, null, 2)} showLineNumbers={false} lang="json" prePadding="p-2" />
                  </div>
                {/if}
              </div>
            {/key}
          {/if}

          <!-- Links -->
          {#if span.links.length > 0}
            <div>
              <div class="flex items-center gap-1.5 mb-2 border-b-2 border-black pb-1">
                <Link2 class="w-3.5 h-3.5 text-primary-700" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-950">Links</span>
                <span class="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-primary-100 border border-primary-400 rounded-sm text-primary-800">{span.links.length}</span>
              </div>
              <div class="space-y-2">
                {#each span.links as link}
                  <div class="bg-white border-2 border-black rounded-base p-2.5 shadow-small space-y-1">
                    <Pill key="Trace ID" value={link.trace_id} textSize="text-xs"/>
                    <Pill key="Span ID" value={link.span_id} textSize="text-xs"/>
                    {#if link.trace_state}
                      <Pill key="State" value={link.trace_state} textSize="text-xs"/>
                    {/if}
                    {#if link.dropped_attributes_count > 0}
                      <div class="text-xs text-warning-600 flex items-center gap-1 font-bold mt-1">
                        <AlertCircle class="w-3 h-3" />
                        {link.dropped_attributes_count} attrs dropped
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          {#if !parsedInput && !parsedOutput && Object.keys(tokenAttrs).length === 0 && !modelAttr && span.links.length === 0}
            <div class="flex flex-col items-center justify-center py-10 text-center text-gray-400">
              <Info class="w-8 h-8 mb-2 opacity-40" />
              <p class="text-xs font-bold uppercase tracking-wide">No LLM or IO data for this span</p>
            </div>
          {/if}
        </div>

      </div>
    {/if}

    <!-- ERRORS TAB -->
    {#if activeTab === 'errors'}
      <div class="p-4">
        {#if !spanHasError && errorEvents.length === 0}
          <div class="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div class="w-12 h-12 border-2 border-black bg-secondary-50 rounded-base shadow-small flex items-center justify-center">
              <AlertCircle class="w-6 h-6 text-secondary-400" />
            </div>
            <p class="text-sm font-bold text-gray-500 uppercase tracking-wide">No errors for this span</p>
          </div>
        {:else}
          <div class="space-y-4">
            <!-- Status message error -->
            {#if spanHasError && span.status_message}
              <div class="bg-error-50 border-2 border-error-500 rounded-base p-3 shadow-small">
                <div class="flex items-center gap-2 mb-2">
                  <AlertCircle class="w-4 h-4 text-error-600" />
                  <span class="text-xs font-black uppercase tracking-wide text-error-700">Span Status Error</span>
                </div>
                <p class="text-xs font-mono text-error-800 whitespace-pre-wrap">{span.status_message}</p>
              </div>
            {/if}

            <!-- Exception events -->
            {#each errorEvents as event}
              {@const traceback = getTraceback(event.attributes)}
              {@const otherAttrs = getNonTracebackAttributes(event.attributes)}
              <div class="bg-white border-2 border-black rounded-base p-3 shadow-small space-y-2">
                <div class="flex items-center gap-2">
                  <AlertCircle class="w-4 h-4 text-error-600 flex-shrink-0" />
                  <span class="text-sm font-black text-gray-900">{event.name}</span>
                </div>
                <Pill key="Timestamp" value={event.timestamp} textSize="text-xs" />
                {#each otherAttrs as attr}
                  <Pill key={attr.key} value={formatAttributeValue(attr.value)} textSize="text-xs" />
                {/each}
                {#if traceback}
                  <div class="mt-2">
                    <div class="flex items-center gap-1 mb-1">
                      <AlertCircle class="w-3.5 h-3.5 text-error-600" />
                      <span class="text-xs font-black text-error-600">Exception Traceback</span>
                    </div>
                    <div class="max-h-56 overflow-y-auto bg-surface-50 border-2 border-error-500 rounded-base shadow-small text-xs">
                      <CodeBlock code={traceback} showLineNumbers={false} lang="python" theme="traceback-theme" />
                    </div>
                  </div>
                {/if}
                {#if event.dropped_attributes_count > 0}
                  <div class="text-xs text-warning-600 flex items-center gap-1 font-bold">
                    <AlertCircle class="w-3 h-3" />
                    {event.dropped_attributes_count} attributes dropped
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    <!-- ATTRIBUTES TAB -->
    {#if activeTab === 'attributes'}
      <div class="p-4 space-y-3">
        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
          <input
            type="text"
            placeholder="Search attributes..."
            bind:value={attrSearch}
            class="w-full pl-8 pr-3 py-1.5 text-xs border-2 border-black rounded-base bg-white font-mono focus:outline-none focus:border-primary-500 shadow-small"
          />
        </div>

        {#if filteredAttributes.length === 0}
          <p class="text-xs text-gray-400 italic text-center py-8">
            {attrSearch ? 'No attributes match your search' : 'No attributes recorded'}
          </p>
        {:else}
          <table class="w-full text-xs border-2 border-black rounded-base overflow-hidden shadow-small">
            <thead>
              <tr class="bg-surface-100 border-b-2 border-black">
                <th class="px-3 py-2 text-left font-black uppercase tracking-wide text-gray-600 w-2/5">Key</th>
                <th class="px-3 py-2 text-left font-black uppercase tracking-wide text-gray-600">Value</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredAttributes as attr, i}
                <tr class="{i % 2 === 0 ? 'bg-white' : 'bg-surface-50'} border-b border-black/10">
                  <td class="px-3 py-2 font-mono font-bold text-primary-800 align-top">{attr.key}</td>
                  <td class="px-3 py-2 font-mono text-black break-all">
                    {#if String(formatAttributeValue(attr.value)).length > 120}
                      <details class="group">
                        <summary class="cursor-pointer list-none">
                          <span>{String(formatAttributeValue(attr.value)).slice(0, 120)}&hellip;</span>
                          <span class="text-primary-600 font-bold ml-1 group-open:hidden">show more</span>
                        </summary>
                        <span class="whitespace-pre-wrap">{formatAttributeValue(attr.value)}</span>
                      </details>
                    {:else}
                      {formatAttributeValue(attr.value)}
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    {/if}

    <!-- EVENTS TAB -->
    {#if activeTab === 'events'}
      <div class="p-4">
        {#if span.events.length === 0}
          <div class="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div class="w-12 h-12 border-2 border-black bg-surface-100 rounded-base shadow-small flex items-center justify-center">
              <Activity class="w-6 h-6 text-gray-300" />
            </div>
            <p class="text-sm font-bold text-gray-500 uppercase tracking-wide">No events for this span</p>
          </div>
        {:else}
          <SpanEvents events={span.events} />
        {/if}
      </div>
    {/if}

  </div>
</div>
