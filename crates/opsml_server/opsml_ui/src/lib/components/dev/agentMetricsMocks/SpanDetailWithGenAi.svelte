<script lang="ts">
  import type { TraceSpan } from '$lib/components/trace/types';
  import type { GenAiSpanRecord } from './types';
  import { formatDuration } from '$lib/components/trace/utils';
  import {
    Activity,
    AlertCircle,
    ArrowLeftRight,
    BadgeCheck,
    Database,
    Info,
    MessageSquare,
    Server,
    Settings2,
    Sparkles,
    Tags,
    Wrench
  } from 'lucide-svelte';
  import { fmtInt, fmtMs } from './format';

  let {
    span,
    genAiSpan = null
  }: {
    span: TraceSpan;
    genAiSpan: GenAiSpanRecord | null;
  } = $props();

  type Tab = 'overview' | 'errors' | 'attributes' | 'reqres' | 'events' | 'resources' | 'genai';
  let activeTab = $state<Tab>('overview');

  $effect(() => {
    span.span_id;
    if (activeTab === 'genai' && !genAiSpan) activeTab = 'overview';
  });

  type SpanGenAiTab = 'messages' | 'eval' | 'params' | 'agent' | 'tool' | 'server' | 'raw';
  let genAiTab = $state<SpanGenAiTab>('messages');

  const tabs = $derived([
    { id: 'overview'   as Tab, label: 'Overview',   Icon: Info,           count: null as number | null },
    { id: 'errors'     as Tab, label: 'Errors',     Icon: AlertCircle,    count: span.status_code === 2 ? 1 : null as number | null },
    { id: 'attributes' as Tab, label: 'Attributes', Icon: Tags,           count: span.attributes.length > 0 ? span.attributes.length : null as number | null },
    { id: 'reqres'     as Tab, label: 'Req / Res',  Icon: ArrowLeftRight, count: null as number | null },
    { id: 'events'     as Tab, label: 'Events',     Icon: Activity,       count: span.events.length > 0 ? span.events.length : null as number | null },
    { id: 'resources'  as Tab, label: 'Resources',  Icon: Server,         count: null as number | null },
    ...(genAiSpan ? [{
      id: 'genai' as Tab,
      label: 'GenAI',
      Icon: Sparkles,
      count: genAiSpan.eval_results.length > 0 ? genAiSpan.eval_results.length : null as number | null
    }] : [])
  ]);

  const genAiSubTabs: { key: SpanGenAiTab; label: string }[] = [
    { key: 'messages', label: 'Messages' },
    { key: 'eval',     label: 'Eval' },
    { key: 'params',   label: 'Request' },
    { key: 'agent',    label: 'Agent' },
    { key: 'tool',     label: 'Tool' },
    { key: 'server',   label: 'Server' },
    { key: 'raw',      label: 'Raw' }
  ];

  function pretty(s: string | null): string {
    if (!s) return '—';
    try { return JSON.stringify(JSON.parse(s), null, 2); }
    catch { return s; }
  }

  function parseMessages(json: string | null): unknown[] | null {
    if (!json) return null;
    try {
      const parsed = JSON.parse(json);
      return Array.isArray(parsed) ? parsed : null;
    } catch { return null; }
  }

  function extractMessageText(msg: unknown): string {
    const m = msg as Record<string, unknown>;
    if (typeof m.content === 'string') return m.content;
    if (Array.isArray(m.content)) {
      return (m.content as Record<string, unknown>[])
        .filter(p => p.type === 'text')
        .map(p => (typeof p.text === 'string' ? p.text : typeof p.content === 'string' ? p.content : ''))
        .filter(Boolean)
        .join('\n');
    }
    if (Array.isArray(m.parts)) {
      return (m.parts as Record<string, unknown>[])
        .filter(p => p.type === 'text')
        .map(p => (typeof p.text === 'string' ? p.text : typeof p.content === 'string' ? p.content : ''))
        .filter(Boolean)
        .join('\n');
    }
    return JSON.stringify(m, null, 2);
  }

  function extractMessageRole(msg: unknown): string {
    const m = msg as Record<string, unknown>;
    return typeof m.role === 'string' ? m.role : 'unknown';
  }
</script>

<div class="flex flex-col h-full bg-surface-50 overflow-hidden">

  <!-- Tab bar -->
  <div class="flex-shrink-0 flex items-center gap-0 border-b border-black/20 bg-surface-50 px-3 pt-2 overflow-x-auto">
    {#each tabs as { id, label, Icon, count }}
      <button
        onclick={() => (activeTab = id)}
        class="flex items-center gap-1.5 px-3 pb-2 pt-0.5 text-[11px] font-black uppercase tracking-wide border-b-2 whitespace-nowrap transition-colors duration-100 ease-out
          {activeTab === id
            ? id === 'genai'
              ? 'border-primary-500 text-primary-700'
              : 'border-primary-600 text-primary-800'
            : 'border-transparent text-primary-600 hover:text-primary-800 hover:border-primary-300'}"
      >
        <Icon class="w-3 h-3" />
        {label}
        {#if count !== null}
          {#if id === 'errors'}
            <span class="px-1.5 py-0.5 rounded-base text-[9px] font-black bg-error-200/40 text-error-700 border border-error-500/40">{count}</span>
          {:else}
            <span class="px-1.5 py-0.5 rounded-base text-[9px] font-black bg-surface-200 text-primary-700 border border-black/20">{count}</span>
          {/if}
        {/if}
      </button>
    {/each}
  </div>

  <!-- Tab panels — single scroll context, overscroll-contain prevents page scroll -->
  <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain">

    <!-- OVERVIEW -->
    {#if activeTab === 'overview'}
      <div class="p-3 space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <h3 class="text-xs font-black text-primary-900 truncate">{span.span_name}</h3>
            <p class="text-[11px] font-mono text-primary-600 mt-0.5">{span.service_name}</p>
          </div>
          <span class="px-2 py-0.5 text-[10px] font-black border uppercase rounded-base flex-shrink-0
            {span.status_code === 2 ? 'bg-error-200/30 text-error-700 border-error-500/40' : span.status_code === 1 ? 'bg-primary-200/20 text-primary-700 border-primary-500/30' : 'bg-surface-200 text-primary-600 border-black/20'}">
            {span.status_code === 2 ? 'ERROR' : span.status_code === 1 ? 'OK' : 'UNSET'}
          </span>
        </div>
        <div class="border border-black/20 rounded-base overflow-hidden">
          <table class="w-full text-[11px]">
            <tbody>
              {#each [
                ['Trace ID',  span.trace_id],
                ['Span ID',   span.span_id],
                ['Parent ID', span.parent_span_id || '—'],
                ['Start',     span.start_time],
                ['End',       span.end_time || '—'],
                ['Duration',  formatDuration(span.duration_ms)],
                ['Kind',      span.span_kind || 'UNSPECIFIED'],
                ['Depth',     `L${span.depth}`],
              ] as row, i}
                <tr class="{i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-100'}">
                  <td class="px-2.5 py-1.5 font-black text-primary-700 uppercase tracking-wide border-b border-black/10 w-24 whitespace-nowrap text-[9px]">{row[0]}</td>
                  <td class="px-2.5 py-1.5 font-mono text-primary-900 border-b border-black/10 break-all">{row[1]}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        {#if genAiSpan}
          <div class="flex items-center gap-2 px-3 py-2 bg-primary-200/10 border border-primary-500/30 rounded-base">
            <Sparkles class="w-3 h-3 text-primary-600 flex-shrink-0" />
            <span class="text-[11px] font-bold text-primary-800">
              {genAiSpan.operation_name ?? 'unknown op'}
              {#if genAiSpan.request_model} · {genAiSpan.request_model}{/if}
              {#if genAiSpan.input_tokens != null} · {fmtInt(genAiSpan.input_tokens)}in / {fmtInt(genAiSpan.output_tokens ?? 0)}out tok{/if}
            </span>
            <button
              class="ml-auto text-[10px] font-black text-primary-600 uppercase hover:text-primary-800"
              onclick={() => (activeTab = 'genai')}
            >view →</button>
          </div>
        {/if}
      </div>

    <!-- ERRORS -->
    {:else if activeTab === 'errors'}
      <div class="flex flex-col items-center justify-center py-12 text-center gap-3 p-4">
        {#if span.status_code === 2}
          <div class="flex items-center gap-2 p-2.5 bg-error-200/20 border border-error-500/40 rounded-base w-full">
            <AlertCircle class="w-4 h-4 text-error-600 flex-shrink-0" />
            <p class="text-[11px] font-mono text-error-700">{span.status_message ?? 'Error status set'}</p>
          </div>
        {:else}
          <AlertCircle class="w-8 h-8 text-primary-700/30" />
          <p class="text-[11px] font-black text-primary-600 uppercase tracking-wide">No errors</p>
        {/if}
      </div>

    <!-- ATTRIBUTES -->
    {:else if activeTab === 'attributes'}
      <div class="p-3">
        <div class="border border-black/20 rounded-base overflow-hidden">
          <div class="px-3 py-1.5 bg-surface-200 border-b border-black/20 flex items-center gap-2">
            <Tags class="w-3 h-3 text-primary-700" />
            <span class="text-[10px] font-black uppercase text-primary-800">{span.attributes.length} attributes</span>
          </div>
          <div class="divide-y divide-black/10">
            {#each span.attributes.slice(0, 12) as attr}
              <div class="px-2.5 py-1.5 flex items-baseline gap-2 text-[11px] font-mono">
                <span class="text-primary-600 shrink-0 text-[10px]">{attr.key}</span>
                <span class="text-primary-900 break-all">{JSON.stringify(attr.value)}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>

    <!-- REQ/RES / EVENTS / RESOURCES (placeholders) -->
    {:else if activeTab === 'reqres' || activeTab === 'events' || activeTab === 'resources'}
      <div class="flex flex-col items-center justify-center py-12 gap-2 text-center p-4">
        <ArrowLeftRight class="w-8 h-8 text-primary-700/30" />
        <div class="text-[11px] font-bold text-primary-600 uppercase italic">Same as existing SpanDetailView — {activeTab}</div>
      </div>

    <!-- ★ GENAI TAB ★ -->
    {:else if activeTab === 'genai' && genAiSpan}
      <!-- Sticky sub-tab bar so it stays visible while the outer div scrolls -->
      <div class="sticky top-0 z-10 flex border-b border-black/20 bg-surface-100 overflow-x-auto">
        {#each genAiSubTabs as t}
          <button
            onclick={() => (genAiTab = t.key)}
            class="px-3 py-1.5 text-[10px] font-black uppercase tracking-wide border-r border-black/10 transition-colors duration-100
              {genAiTab === t.key ? 'bg-primary-200/30 text-primary-900' : 'text-primary-600 hover:text-primary-800 hover:bg-surface-200'}"
          >
            {t.label}
          </button>
        {/each}
      </div>

      <!-- All genai content flows naturally — outer overflow-y-auto handles scroll -->
      <div class="p-3">

        <!-- Messages -->
        {#if genAiTab === 'messages'}
          <div class="space-y-4">

            {#if genAiSpan.system_instructions}
              <div>
                <div class="text-[10px] font-black uppercase text-primary-700 mb-1.5">system_instructions</div>
                <div class="border border-black/20 rounded-base overflow-hidden">
                  <div class="flex items-center gap-1.5 px-2 py-1 border-b border-black/10 bg-surface-200">
                    <span class="text-[9px] font-black uppercase tracking-widest text-primary-600">system</span>
                  </div>
                  <div class="px-2.5 py-2 bg-surface-50">
                    <p class="text-[11px] font-mono whitespace-pre-wrap text-primary-900 leading-relaxed">{genAiSpan.system_instructions}</p>
                  </div>
                </div>
              </div>
            {/if}

            {#if genAiSpan.input_messages}
              {@const msgs = parseMessages(genAiSpan.input_messages)}
              <div>
                <div class="text-[10px] font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1">
                  <MessageSquare class="w-3 h-3" /> input_messages
                  {#if genAiSpan.input_tokens != null}
                    <span class="font-mono text-primary-600 ml-1">{fmtInt(genAiSpan.input_tokens)} tok</span>
                  {/if}
                </div>
                {#if msgs}
                  <div class="space-y-2">
                    {#each msgs as msg, i}
                      {@const role = extractMessageRole(msg)}
                      {@const text = extractMessageText(msg)}
                      <div class="border border-black/20 rounded-base overflow-hidden">
                        <div class="flex items-center gap-1.5 px-2 py-1 border-b border-black/10 bg-surface-200">
                          <span class="text-[9px] font-black uppercase tracking-widest text-primary-700">{role}</span>
                          <span class="ml-auto text-[9px] font-mono text-primary-600">#{i + 1}</span>
                        </div>
                        <div class="px-2.5 py-2 bg-surface-50">
                          <p class="text-[11px] font-mono whitespace-pre-wrap text-primary-900 leading-relaxed">{text}</p>
                        </div>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <pre class="text-[11px] bg-surface-100 border border-black/20 rounded-base p-2 overflow-x-auto font-mono text-primary-900">{pretty(genAiSpan.input_messages)}</pre>
                {/if}
              </div>
            {/if}

            {#if genAiSpan.output_messages}
              {@const msgs = parseMessages(genAiSpan.output_messages)}
              <div>
                <div class="text-[10px] font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1">
                  <MessageSquare class="w-3 h-3" /> output_messages
                  {#if genAiSpan.output_tokens != null}
                    <span class="font-mono text-primary-600 ml-1">{fmtInt(genAiSpan.output_tokens)} tok</span>
                  {/if}
                </div>
                {#if msgs}
                  <div class="space-y-2">
                    {#each msgs as msg, i}
                      {@const role = extractMessageRole(msg)}
                      {@const text = extractMessageText(msg)}
                      <div class="border border-black/20 rounded-base overflow-hidden">
                        <div class="flex items-center gap-1.5 px-2 py-1 border-b border-black/10 bg-surface-200">
                          <span class="text-[9px] font-black uppercase tracking-widest text-primary-700">{role}</span>
                          <span class="ml-auto text-[9px] font-mono text-primary-600">#{i + 1}</span>
                        </div>
                        <div class="px-2.5 py-2 bg-surface-50">
                          <p class="text-[11px] font-mono whitespace-pre-wrap text-primary-900 leading-relaxed">{text}</p>
                        </div>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <pre class="text-[11px] bg-surface-100 border border-black/20 rounded-base p-2 overflow-x-auto font-mono text-primary-900">{pretty(genAiSpan.output_messages)}</pre>
                {/if}
              </div>
            {/if}

            {#if genAiSpan.tool_definitions}
              <div>
                <div class="text-[10px] font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1">
                  <Database class="w-3 h-3" /> tool_definitions
                </div>
                <pre class="text-[11px] bg-surface-100 border border-black/20 rounded-base p-2 overflow-x-auto font-mono text-primary-900">{pretty(genAiSpan.tool_definitions)}</pre>
              </div>
            {/if}

            {#if !genAiSpan.system_instructions && !genAiSpan.input_messages && !genAiSpan.output_messages}
              <div class="text-center text-primary-600 italic text-[11px] py-6">no message content captured for this span</div>
            {/if}
          </div>

        <!-- Eval -->
        {:else if genAiTab === 'eval'}
          {#if genAiSpan.eval_results.length === 0}
            <div class="text-center text-primary-600 italic text-[11px] py-6 flex flex-col items-center gap-2">
              <BadgeCheck class="w-8 h-8 opacity-30" />
              no eval_results recorded for this span
            </div>
          {:else}
            <div class="space-y-2">
              {#each genAiSpan.eval_results as e}
                <div class="border border-black/20 rounded-base bg-surface-100 p-3">
                  <div class="flex items-center justify-between mb-1">
                    <div class="flex items-center gap-2">
                      <BadgeCheck class="w-3.5 h-3.5 text-primary-700" />
                      <span class="font-black text-primary-900 text-[11px]">{e.name}</span>
                      {#if e.score_label}
                        <span class="px-1.5 py-0.5 bg-surface-200 border border-black/20 rounded-base text-[9px] font-bold text-primary-700">{e.score_label}</span>
                      {/if}
                    </div>
                    {#if e.score_value != null}
                      <span class="font-mono font-black text-primary-900 text-sm">{e.score_value}</span>
                    {/if}
                  </div>
                  {#if e.explanation}
                    <p class="text-[11px] text-primary-800 mt-1">{e.explanation}</p>
                  {/if}
                  {#if e.response_id}
                    <div class="text-[10px] font-mono text-primary-600 mt-1">response_id: {e.response_id}</div>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}

        <!-- Request params -->
        {:else if genAiTab === 'params'}
          <div class="space-y-2">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5">
              {#each [
                { k: 'request_model',      v: genAiSpan.request_model },
                { k: 'response_model',     v: genAiSpan.response_model },
                { k: 'response_id',        v: genAiSpan.response_id },
                { k: 'temperature',        v: genAiSpan.request_temperature },
                { k: 'max_tokens',         v: genAiSpan.request_max_tokens },
                { k: 'top_p',              v: genAiSpan.request_top_p },
                { k: 'seed',               v: genAiSpan.request_seed },
                { k: 'freq_penalty',       v: genAiSpan.request_frequency_penalty },
                { k: 'presence_penalty',   v: genAiSpan.request_presence_penalty },
                { k: 'choice_count',       v: genAiSpan.request_choice_count },
                { k: 'finish_reasons',     v: genAiSpan.finish_reasons.join(', ') || null },
                { k: 'output_type',        v: genAiSpan.output_type },
                { k: 'input_tokens',       v: genAiSpan.input_tokens },
                { k: 'output_tokens',      v: genAiSpan.output_tokens },
                { k: 'cache_creation_tok', v: genAiSpan.cache_creation_input_tokens },
                { k: 'cache_read_tok',     v: genAiSpan.cache_read_input_tokens },
              ] as row}
                <div class="border border-black/20 rounded-base bg-surface-100 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest flex items-center gap-1">
                    <Settings2 class="w-2.5 h-2.5" /> {row.k}
                  </div>
                  <div class="text-[11px] font-mono text-primary-900 leading-tight">{row.v ?? '—'}</div>
                </div>
              {/each}
            </div>
            {#if genAiSpan.request_stop_sequences.length > 0}
              <div class="border border-black/20 rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase">stop_sequences</div>
                <div class="text-[11px] font-mono text-primary-900">{genAiSpan.request_stop_sequences.join(' · ')}</div>
              </div>
            {/if}
          </div>

        <!-- Agent context -->
        {:else if genAiTab === 'agent'}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1.5">
            {#each [
              { k: 'agent_name',        v: genAiSpan.agent_name },
              { k: 'agent_id',          v: genAiSpan.agent_id },
              { k: 'agent_version',     v: genAiSpan.agent_version },
              { k: 'agent_description', v: genAiSpan.agent_description },
              { k: 'conversation_id',   v: genAiSpan.conversation_id },
              { k: 'data_source_id',    v: genAiSpan.data_source_id },
              { k: 'label',             v: genAiSpan.label },
              { k: 'operation_name',    v: genAiSpan.operation_name },
              { k: 'provider_name',     v: genAiSpan.provider_name },
            ] as row}
              <div class="border border-black/20 rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase tracking-widest">{row.k}</div>
                <div class="text-[11px] font-mono text-primary-900 break-all leading-tight">{row.v ?? '—'}</div>
              </div>
            {/each}
          </div>

        <!-- Tool -->
        {:else if genAiTab === 'tool'}
          <div class="space-y-2">
            <div class="grid grid-cols-3 gap-1.5">
              {#each [
                { k: 'tool_name',    v: genAiSpan.tool_name },
                { k: 'tool_type',    v: genAiSpan.tool_type },
                { k: 'tool_call_id', v: genAiSpan.tool_call_id },
              ] as row}
                <div class="border border-black/20 rounded-base bg-surface-100 px-2 py-1">
                  <div class="text-[9px] font-black text-primary-700 uppercase flex items-center gap-1">
                    <Wrench class="w-2.5 h-2.5" /> {row.k}
                  </div>
                  <div class="text-[11px] font-mono text-primary-900 break-all">{row.v ?? '—'}</div>
                </div>
              {/each}
            </div>
            {#if !genAiSpan.tool_name && !genAiSpan.tool_call_id}
              <div class="text-center text-primary-600 italic text-[11px] py-4">no tool data for this span</div>
            {/if}
          </div>

        <!-- Server -->
        {:else if genAiTab === 'server'}
          <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5">
            {#each [
              { k: 'server_address',       v: genAiSpan.server_address },
              { k: 'server_port',          v: genAiSpan.server_port },
              { k: 'openai_api_type',      v: genAiSpan.openai_api_type },
              { k: 'openai_service_tier',  v: genAiSpan.openai_service_tier },
            ] as row}
              <div class="border border-black/20 rounded-base bg-surface-100 px-2 py-1">
                <div class="text-[9px] font-black text-primary-700 uppercase flex items-center gap-1">
                  <Server class="w-2.5 h-2.5" /> {row.k}
                </div>
                <div class="text-[11px] font-mono break-all text-primary-900">{row.v ?? '—'}</div>
              </div>
            {/each}
          </div>

        <!-- Raw -->
        {:else if genAiTab === 'raw'}
          <pre class="text-[10px] font-mono bg-surface-100 border border-black/20 rounded-base p-2 overflow-x-auto text-primary-900">{JSON.stringify(genAiSpan, null, 2)}</pre>
        {/if}

      </div>
    {/if}

  </div>
</div>
