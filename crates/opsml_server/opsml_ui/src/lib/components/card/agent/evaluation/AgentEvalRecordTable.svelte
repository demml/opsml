<!--
  AgentEvalRecordTable.svelte
  ──────────────────────────
  Displays merged evaluation records from all agent-associated prompt cards.
  Receives a flat sorted list + pagination booleans from AgentEvalDashboard.
  Manages its own row-detail sidebar.
-->
<script lang="ts">
  import type { RecordWithAgent } from './types';
  import type { Status } from '$lib/components/scouter/genai/types';
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import GenAIEvalRecordSideBar from '$lib/components/scouter/genai/record/GenAIEvalRecordSideBar.svelte';

  let {
    records,
    hasNext,
    hasPrevious,
    onPageChange,
    isRefreshing = false,
  }: {
    records: RecordWithAgent[];
    hasNext: boolean;
    hasPrevious: boolean;
    onPageChange: (direction: string) => void;
    isRefreshing?: boolean;
  } = $props();

  let selectedRecord = $state<RecordWithAgent | null>(null);

  function fmt(ts: string): string {
    return new Date(ts).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true,
    });
  }

  function fmtDur(ms: number | null): string {
    if (ms === null) return '—';
    const s = ms / 1000;
    return s < 1 ? `${ms}ms` : `${s.toFixed(2)}s`;
  }

  function statusBadge(status: Status): string {
    const map: Record<string, string> = {
      Pending:    'bg-warning-100 border-warning-900 text-warning-900',
      Processing: 'bg-primary-100 border-primary-900 text-primary-900',
      Processed:  'bg-secondary-100 border-secondary-900 text-secondary-900',
      Failed:     'bg-error-100 border-error-900 text-error-900',
    };
    return map[status] ?? 'bg-primary-100 border-primary-900 text-primary-900';
  }

  function statusBar(status: Status): string {
    const map: Record<string, string> = {
      Processed: 'bg-secondary-600', Processing: 'bg-primary-600',
      Pending: 'bg-warning-600', Failed: 'bg-error-600',
    };
    return map[status] ?? 'bg-surface-200';
  }

  const thClass = 'px-3 py-2 text-center text-xss font-black uppercase tracking-wider text-primary-700 whitespace-nowrap';
  const tdClass = 'px-3 py-2.5 text-center align-middle';
</script>

<div class="overflow-auto max-h-[500px] transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none' : ''}">
  {#if records.length === 0}
    <div class="flex items-center justify-center py-12">
      <p class="text-sm font-bold text-black/50">No evaluation records to display</p>
    </div>
  {:else}
    <table class="min-w-max w-full text-sm border-collapse">
      <thead class="bg-surface-200 border-b-2 border-black sticky top-0 z-10">
        <tr>
          <th class={thClass}>Prompt</th>
          <th class={thClass}>ID</th>
          <th class={thClass}>Created</th>
          <th class={thClass}>Status</th>
          <th class={thClass}>Entity Type</th>
          <th class={thClass}>Proc. Started</th>
          <th class={thClass}>Proc. Ended</th>
          <th class={thClass}>Duration</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-black/10">
        {#each records as record, i}
          <tr
            class="cursor-pointer transition-colors duration-100 group
                   {i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-100'} hover:bg-primary-50"
            onclick={() => { selectedRecord = record; }}
          >
            <td class={tdClass}>
              <span class="px-2 py-0.5 rounded-base border border-black bg-primary-100 text-primary-950
                           text-xss font-black uppercase tracking-wider inline-block max-w-[150px] truncate"
                    title={record._agentName}>
                {record._agentName}
              </span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black/60 group-hover:text-black font-bold">
                {record.uid.slice(0, 8)}
              </span>
            </td>
            <td class={tdClass}>
              <div class="flex items-center justify-center gap-1.5">
                <div class="w-1.5 h-4 rounded-sm flex-shrink-0 {statusBar(record.status)}"></div>
                <span class="text-xs text-black font-mono whitespace-nowrap">{fmt(record.created_at)}</span>
              </div>
            </td>
            <td class={tdClass}>
              <span class="px-2 py-0.5 rounded-base border text-xss font-black uppercase {statusBadge(record.status)}">
                {record.status}
              </span>
            </td>
            <td class={tdClass}>
              <span class="px-2 py-0.5 rounded-base border border-primary-900 bg-primary-100 text-primary-900 text-xss font-bold">
                {record.entity_type}
              </span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black/60 whitespace-nowrap">
                {record.processing_started_at ? fmt(record.processing_started_at) : '—'}
              </span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black/60 whitespace-nowrap">
                {record.processing_ended_at ? fmt(record.processing_ended_at) : '—'}
              </span>
            </td>
            <td class={tdClass}>
              <span class="text-xs font-mono text-black">{fmtDur(record.processing_duration)}</span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

{#if records.length > 0}
  <div class="border-t-2 border-black bg-surface-200 p-2 flex justify-center gap-2 items-center">
    <button
      class="btn bg-surface-50 border-black border-2 shadow-small shadow-click-small h-9 px-3
             flex items-center justify-center transition-transform duration-100 ease-out
             disabled:opacity-40 disabled:pointer-events-none"
      onclick={() => onPageChange('previous')}
      disabled={!hasPrevious}
    >
      <ArrowLeft class="w-4 h-4 text-primary-700" />
    </button>
    <button
      class="btn bg-surface-50 border-black border-2 shadow-small shadow-click-small h-9 px-3
             flex items-center justify-center transition-transform duration-100 ease-out
             disabled:opacity-40 disabled:pointer-events-none"
      onclick={() => onPageChange('next')}
      disabled={!hasNext}
    >
      <ArrowRight class="w-4 h-4 text-primary-700" />
    </button>
  </div>
{/if}

{#if selectedRecord}
  <GenAIEvalRecordSideBar
    selectedRecord={selectedRecord}
    onClose={() => { selectedRecord = null; }}
  />
{/if}
