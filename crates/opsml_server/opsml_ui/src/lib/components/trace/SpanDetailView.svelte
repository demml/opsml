<script lang="ts">
  import { type TraceSpan, type Attribute } from './types';
  import {
    formatDuration,
    formatAttributeValue,
    hasSpanError,
    getHttpStatusCode,
    parseSpanJson
  } from './utils';
  import {
    Info, Tags, Activity, Link2, AlertCircle, FileJson,
    ChevronDown, ChevronUp, Copy, Check, Search, Server, ArrowLeftRight
  } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import SpanEvents from './SpanEvents.svelte';
  import { EXCEPTION_TRACEBACK } from './types';

  let {
    span,
    onSpanSelect,
    allSpans,
    slowestSpan,
    resourceAttributes = [],
  }: {
    span: TraceSpan;
    onSpanSelect: (span: TraceSpan) => void;
    allSpans: TraceSpan[];
    slowestSpan?: TraceSpan | null;
    resourceAttributes?: Attribute[];
  } = $props();

  // ─── Derived values ────────────────────────────────────────────────────────

  const spanHasError = $derived(hasSpanError(span));
  const httpStatusCode = $derived(getHttpStatusCode(span));
  const parsedInput = $derived(parseSpanJson(span.input));
  const parsedOutput = $derived(parseSpanJson(span.output));
  const spanMap = $derived(new Map(allSpans.map(s => [s.span_id, s])));
  const isSlowest = $derived(slowestSpan && span.span_id === slowestSpan.span_id);
  let copied = $state(false);
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

  // ─── Request / Response extraction ─────────────────────────────────────────
  // Scan all span attributes for keys containing "request" or "response".
  // Values may be raw JSON strings — attempt to parse them for pretty display.

  type ReqResEntry = { key: string; label: string; kind: 'request' | 'response'; parsed: unknown };

  function tryParseJson(val: unknown): unknown {
    if (typeof val === 'string') {
      try { return JSON.parse(val); } catch { /* not JSON */ }
    }
    return val;
  }

  function keyLabel(key: string): string {
    // e.g. "gcp.vertex.agent.llm_request" → "LLM Request"
    const segment = key.split('.').pop() ?? key;
    return segment.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  const reqResEntries = $derived((() => {
    const entries: ReqResEntry[] = [];
    for (const attr of span.attributes) {
      const k = attr.key.toLowerCase();
      if (k.includes('request')) {
        entries.push({ key: attr.key, label: keyLabel(attr.key), kind: 'request', parsed: tryParseJson(attr.value) });
      } else if (k.includes('response')) {
        entries.push({ key: attr.key, label: keyLabel(attr.key), kind: 'response', parsed: tryParseJson(attr.value) });
      }
    }
    // requests first, then responses
    return entries.sort((a, b) => a.kind === b.kind ? 0 : a.kind === 'request' ? -1 : 1);
  })());

  // Collapsed state per req/res entry key
  let collapsedReqRes = $state<Set<string>>(new Set());

  function toggleReqRes(key: string) {
    const next = new Set(collapsedReqRes);
    if (next.has(key)) next.delete(key); else next.add(key);
    collapsedReqRes = next;
  }

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

  $effect(() => {
    // Access span.span_id to track span identity; reset all per-span UI state on change
    span.span_id;
    collapsedReqRes = new Set();
    attrSearch = '';
  });

  function copyJson(rawJson: string) {
    navigator.clipboard.writeText(rawJson);
    copied = true;
    setTimeout(() => copied = false, 2000);
  }

  // ─── Tab state ─────────────────────────────────────────────────────────────

  type Tab = 'overview' | 'errors' | 'attributes' | 'reqres' | 'events' | 'resources';
  let activeTab = $state<Tab>('overview');

  const tabs = $derived([
    { id: 'overview'   as Tab, label: 'Overview',    Icon: Info,            count: null as number | null },
    { id: 'errors'     as Tab, label: 'Errors',      Icon: AlertCircle,     count: errorCount > 0 ? errorCount : null as number | null },
    { id: 'attributes' as Tab, label: 'Attributes',  Icon: Tags,            count: span.attributes.length > 0 ? span.attributes.length : null as number | null },
    { id: 'reqres'     as Tab, label: 'Req / Res',   Icon: ArrowLeftRight,  count: reqResEntries.length > 0 ? reqResEntries.length : null as number | null },
    { id: 'events'     as Tab, label: 'Events',      Icon: Activity,        count: span.events.length > 0 ? span.events.length : null as number | null },
    { id: 'resources'  as Tab, label: 'Resources',   Icon: Server,          count: resourceAttributes.length > 0 ? resourceAttributes.length : null as number | null },
  ]);

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
    'bg-surface-200 text-primary-700 border-primary-400'
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

  /** Render a group of attributes as a JSON object codeblock */
  function attrsToJson(attrs: Attribute[]): string {
    const obj: Record<string, unknown> = {};
    for (const a of attrs) obj[a.key] = a.value;
    return JSON.stringify(obj, null, 2);
  }

  const accentBarColor = $derived(spanHasError ? 'bg-error-600' : span.status_code === 1 ? 'bg-secondary-500' : 'bg-gray-400');
</script>

<div class="flex flex-col h-full bg-surface-50 overflow-hidden">

  <!-- ─── Sub-tab bar ─────────────────────────────────────────────────────── -->
  <div class="flex-shrink-0 flex items-center gap-0 border-b-2 border-black bg-surface-50 px-3 pt-2 overflow-x-auto">
    {#each tabs as { id, label, Icon, count }}
      <button
        onclick={() => activeTab = id}
        class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-xs font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
          {activeTab === id ? 'border-primary-600 text-primary-800' : 'border-transparent text-primary-700/60 hover:text-primary-800 hover:border-primary-300'}"
      >
        <Icon class="w-3 h-3" />
        {label}
        {#if count !== null}
          {#if id === 'errors'}
            <span class="px-1.5 py-0.5 rounded-base text-[10px] font-black bg-error-100 text-error-800 border border-error-400">{count}</span>
          {:else}
            <span class="px-1.5 py-0.5 rounded-base text-[10px] font-black bg-primary-100 text-primary-800 border border-primary-300">{count}</span>
          {/if}
        {/if}
      </button>
    {/each}
  </div>

  <!-- ─── Tab panels ──────────────────────────────────────────────────────── -->
  <div class="flex-1 overflow-y-auto">

    <!-- OVERVIEW TAB -->
    {#if activeTab === 'overview'}
      <div class="flex flex-col gap-0 h-full divide-y-2 divide-black">


        <!-- Core span metadata -->
        <div class="p-4 space-y-3">
          <!-- Span name + status row -->
       
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <h3 class="text-sm font-black text-black leading-tight truncate">{span.span_name}</h3>
              <p class="text-xs text-primary-700 font-mono mt-0.5 truncate">{span.service_name}</p>
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
            <div class="flex items-start gap-2 p-2.5 bg-error-100 border-2 border-error-600 rounded-base shadow-small">
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
                  <tr class="{i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-200'}">
                    <td class="px-2.5 py-1.5 font-black text-primary-800 uppercase tracking-wide border-b border-black/10 w-28 flex-shrink-0 whitespace-nowrap">{row[0]}</td>
                    <td class="px-2.5 py-1.5 font-mono text-black border-b border-black/10 break-all">
                      {#if row[0] === 'Span ID'}
                        <div class="flex items-center gap-1.5">
                          <span class="truncate">{span.span_id}</span>
                          <button
                            onclick={copySpanId}
                            class="flex-shrink-0 p-0.5 rounded border border-black/20 bg-surface-50 hover:bg-surface-200 transition-colors"
                            aria-label="Copy span ID"
                          >
                            {#if copiedSpanId}
                              <Check class="w-3 h-3 text-secondary-600" />
                            {:else}
                              <Copy class="w-3 h-3 text-primary-400" />
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
                <span class="ml-auto text-xs font-mono text-primary-500">{span.path.length} hops</span>
              </div>
              <div class="flex flex-wrap gap-1.5 items-center">
                {#each span.path as seg, i}
                  <button
                    class="px-2 py-0.5 bg-primary-100 border border-primary-600 text-xs font-mono text-primary-900 shadow-small shadow-hover-small transition-all rounded-sm"
                    onclick={() => handlePathSegmentClick(seg)}
                    title={seg}
                  >{seg.slice(0, 8)}</button>
                  {#if i < span.path.length - 1}
                    <span class="text-primary-400 text-xs">→</span>
                  {/if}
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- LLM / IO data -->
        <div class="p-4 space-y-3 bg-surface-50">

          <!-- Model + tokens (if present) -->
          {#if modelAttr || Object.keys(tokenAttrs).length > 0}
            <div class="space-y-2">
              <h4 class="text-xs font-black uppercase tracking-wide text-primary-950 border-b-2 border-black pb-1">LLM Details</h4>
              {#if modelAttr}
                <div class="flex items-center gap-2 p-2 bg-surface-50 border-2 border-black rounded-base shadow-small">
                  <span class="text-xs font-bold text-primary-700 w-14 flex-shrink-0">Model</span>
                  <span class="text-xs font-mono text-black font-bold">{modelAttr}</span>
                </div>
              {/if}
              {#if Object.keys(tokenAttrs).length > 0}
                <div class="grid grid-cols-3 gap-1.5">
                  {#each Object.entries(tokenAttrs) as [key, val]}
                    <div class="p-2 bg-surface-50 border-2 border-black rounded-base shadow-small text-center">
                      <div class="text-xs font-mono font-black text-primary-800">{val}</div>
                      <div class="text-[10px] font-bold text-primary-600 uppercase tracking-wide mt-0.5 truncate">{key.split('.').pop()}</div>
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
                  class="w-full flex items-center gap-2 px-2 py-1.5 mb-1.5 border-2 border-primary-400 bg-primary-50 rounded-base cursor-pointer hover:bg-primary-100 transition-colors text-primary-800"
                  onclick={() => showInput = !showInput}
                >
                  <FileJson class="w-3.5 h-3.5 text-primary-700" />
                  <span class="text-xs font-black uppercase tracking-wide">Input</span>
                  <span class="ml-auto">
                    {#if showInput}<ChevronUp class="w-3.5 h-3.5 text-primary-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-primary-500"/>{/if}
                  </span>
                </button>
                {#if showInput}
                  <div class="bg-surface-50 rounded-base border-2 border-black shadow-small text-xs overflow-hidden">
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
                  class="w-full flex items-center gap-2 px-2 py-1.5 mb-1.5 border-2 border-primary-400 bg-primary-50 rounded-base cursor-pointer hover:bg-primary-100 transition-colors text-primary-800"
                  onclick={() => showOutput = !showOutput}
                >
                  <FileJson class="w-3.5 h-3.5 text-primary-700" />
                  <span class="text-xs font-black uppercase tracking-wide">Output</span>
                  <span class="ml-auto">
                    {#if showOutput}<ChevronUp class="w-3.5 h-3.5 text-primary-500"/>{:else}<ChevronDown class="w-3.5 h-3.5 text-primary-500"/>{/if}
                  </span>
                </button>
                {#if showOutput}
                  <div class="bg-surface-50 rounded-base border-2 border-black shadow-small text-xs overflow-hidden">
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
                  <div class="bg-surface-50 border-2 border-black rounded-base p-2.5 shadow-small space-y-1">
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
            <div class="flex flex-col items-center justify-center py-10 text-center text-primary-400">
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
            <div class="w-12 h-12 border-2 border-black bg-secondary-100 rounded-base shadow-small flex items-center justify-center">
              <AlertCircle class="w-6 h-6 text-secondary-500" />
            </div>
            <p class="text-sm font-bold text-primary-600 uppercase tracking-wide">No errors for this span</p>
          </div>
        {:else}
          <div class="space-y-4">
            <!-- Status message error -->
            {#if spanHasError && span.status_message}
              <div class="bg-error-100 border-2 border-error-600 rounded-base p-3 shadow-small">
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
              <div class="bg-surface-50 border-2 border-black rounded-base p-3 shadow-small space-y-2">
                <div class="flex items-center gap-2">
                  <AlertCircle class="w-4 h-4 text-error-600 flex-shrink-0" />
                  <span class="text-sm font-black text-black">{event.name}</span>
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
                    <div class="max-h-56 overflow-y-auto bg-surface-50 border-2 border-error-600 rounded-base shadow-small text-xs">
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
      {#key span.span_id}
      <div class="p-4 space-y-3">
        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-primary-400 pointer-events-none" />
          <input
            type="text"
            placeholder="Filter attributes..."
            bind:value={attrSearch}
            class="w-full pl-8 pr-3 py-1.5 text-xs border-2 border-black rounded-base bg-surface-50 font-mono focus:outline-none focus:bg-primary-50 focus:shadow-small shadow-small"
          />
        </div>

        {#if filteredAttributes.length === 0}
          <p class="text-xs text-primary-400 italic text-center py-8">
            {attrSearch ? 'No attributes match your filter' : 'No attributes recorded'}
          </p>
        {:else}
          <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
            <div class="flex items-center justify-between px-3 py-2 bg-primary-100 border-b-2 border-black">
              <div class="flex items-center gap-2">
                <Tags class="w-3.5 h-3.5 text-primary-700" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-900">All Attributes</span>
                <span class="px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-primary-200 border border-primary-400 text-primary-800">
                  {filteredAttributes.length}
                </span>
              </div>
              <button
                class="btn btn-sm bg-white border-2 border-black shadow-small hover:bg-slate-50 active:translate-y-[2px] active:shadow-none transition-all p-1.5"
                onclick={() => copyJson(attrsToJson(filteredAttributes))}
                aria-label="Copy all attributes"
              >
                <Copy class="w-4 h-4" color="black" />
              </button>
            </div>
            <div class="bg-surface-50 text-xs overflow-hidden">
              <CodeBlock code={attrsToJson(filteredAttributes)} showLineNumbers={false} lang="json" prePadding="p-3" />
            </div>
          </div>
        {/if}
      </div>
      {/key}
    {/if}

    <!-- REQ / RES TAB -->
    {#if activeTab === 'reqres'}
      {#key span.span_id}
      <div class="p-4 space-y-3">
        {#if reqResEntries.length === 0}
          <div class="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div class="w-12 h-12 border-2 border-black bg-surface-200 rounded-base shadow-small flex items-center justify-center">
              <ArrowLeftRight class="w-6 h-6 text-primary-300" />
            </div>
            <p class="text-sm font-bold text-primary-600 uppercase tracking-wide">No request or response data</p>
          </div>
        {:else}
          <div class="space-y-2">
            {#each reqResEntries as entry}
              {@const isCollapsed = collapsedReqRes.has(entry.key)}
              {@const isRequest = entry.kind === 'request'}
              <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
                <!-- Entry header -->
                <button
                  onclick={() => toggleReqRes(entry.key)}
                  class="w-full flex items-center justify-between px-3 py-2 transition-colors duration-100 border-b-2 border-black
                    {isRequest ? 'bg-primary-100 hover:bg-primary-200' : 'bg-secondary-100 hover:bg-secondary-200'}"
                >
                  <div class="flex items-center gap-2">
                    <ArrowLeftRight class="w-3.5 h-3.5 {isRequest ? 'text-primary-700' : 'text-secondary-700'}" />
                    <span class="text-xs font-black uppercase tracking-wide {isRequest ? 'text-primary-900' : 'text-secondary-900'}">{entry.label}</span>
                    <span class="px-1.5 py-0.5 rounded-sm text-[10px] font-bold border
                      {isRequest
                        ? 'bg-primary-200 border-primary-400 text-primary-800'
                        : 'bg-secondary-200 border-secondary-500 text-secondary-800'}">
                      {isRequest ? 'request' : 'response'}
                    </span>
                    <span class="text-[10px] font-mono text-primary-400 truncate max-w-32">{entry.key}</span>
                  </div>
                  {#if isCollapsed}
                    <ChevronDown class="w-3.5 h-3.5 {isRequest ? 'text-primary-600' : 'text-secondary-600'}" />
                  {:else}
                    <ChevronUp class="w-3.5 h-3.5 {isRequest ? 'text-primary-600' : 'text-secondary-600'}" />
                  {/if}
                </button>
                <!-- JSON / value body -->
                {#if !isCollapsed}
                  {@const displayJson = typeof entry.parsed === 'string'
                    ? entry.parsed
                    : JSON.stringify(entry.parsed, null, 2)}
                  <div class="bg-surface-50 text-xs overflow-hidden relative">
                    <button
                      class="absolute p-2 top-2 right-4 btn btn-sm bg-white border-2 border-black shadow-small z-20 hover:bg-slate-50 active:translate-y-[2px] active:shadow-none transition-all"
                      onclick={() => copyJson(displayJson)}
                      aria-label="Copy JSON"
                    >
                      <Copy class="w-4 h-4" color="black" />
                    </button>
                    <div class="bg-surface-50 text-xs overflow-hidden">
                      <CodeBlock code={displayJson} showLineNumbers={false} lang="json" prePadding="p-3" />
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
      {/key}
    {/if}

    <!-- EVENTS TAB -->
    {#if activeTab === 'events'}
      <div class="p-4">
        {#if span.events.length === 0}
          <div class="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div class="w-12 h-12 border-2 border-black bg-surface-200 rounded-base shadow-small flex items-center justify-center">
              <Activity class="w-6 h-6 text-primary-300" />
            </div>
            <p class="text-sm font-bold text-primary-600 uppercase tracking-wide">No events for this span</p>
          </div>
        {:else}
          <SpanEvents events={span.events} />
        {/if}
      </div>
    {/if}

    <!-- RESOURCES TAB -->
    {#if activeTab === 'resources'}
      <div class="p-4 space-y-3">
        {#if resourceAttributes.length === 0}
          <div class="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div class="w-12 h-12 border-2 border-black bg-surface-200 rounded-base shadow-small flex items-center justify-center">
              <Server class="w-6 h-6 text-primary-300" />
            </div>
            <p class="text-sm font-bold text-primary-600 uppercase tracking-wide">No resource attributes</p>
          </div>
        {:else}
          <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
            <div class="flex items-center justify-between px-3 py-2 bg-secondary-100 border-b-2 border-black">
              <div class="flex items-center gap-2">
                <Server class="w-3.5 h-3.5 text-secondary-700" />
                <span class="text-xs font-black uppercase tracking-wide text-secondary-900">All Resources</span>
                <span class="px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-secondary-200 border border-secondary-500 text-secondary-800">
                  {resourceAttributes.length}
                </span>
              </div>
              <button
                class="btn btn-sm bg-white border-2 border-black shadow-small hover:bg-slate-50 active:translate-y-[2px] active:shadow-none transition-all p-1.5"
                onclick={() => copyJson(attrsToJson(resourceAttributes))}
                aria-label="Copy all resources"
              >
                <Copy class="w-4 h-4" color="black" />
              </button>
            </div>
            <div class="bg-surface-50 text-xs overflow-hidden">
              <CodeBlock code={attrsToJson(resourceAttributes)} showLineNumbers={false} lang="json" prePadding="p-3" />
            </div>
          </div>
        {/if}
      </div>
    {/if}

  </div>
</div>
