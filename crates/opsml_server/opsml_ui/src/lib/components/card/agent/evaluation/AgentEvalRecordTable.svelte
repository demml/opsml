<!--
  AgentEvalRecordTable.svelte
  ──────────────────────────
  Displays merged evaluation records from all agent-associated prompt cards.
  Receives a flat sorted list + pagination booleans from AgentEvalDashboard.
  Manages its own row-detail sidebar.

  Structure mirrors EvalRecordTable exactly (the proven working pattern):
    overflow-hidden outer → overflow-auto flex-1 scroll container → min-w forced inner
  The parent (AgentEvalDashboard) must supply flex flex-col on the wrapper div.
-->
<script lang="ts">
  import type { RecordWithAgent } from './types';
  import type { Status } from '$lib/components/scouter/genai/types';
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import EvalRecordSideBar from '$lib/components/scouter/genai/record/EvalRecordSideBar.svelte';

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
  let isSelected = $state(false);

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

  function selectRecord(record: RecordWithAgent) {
    selectedRecord = record;
    isSelected = true;
  }

  function handleClosePanel() {
    selectedRecord = null;
    isSelected = false;
  }

  // Prompt column prepended before ID; 1fr on Entity Type consumes whitespace.
  // min-w-[1050px] = EvalRecordTable's 900px + ~150px for the Prompt column.
  const gridLayout = "grid-template-columns: 140px 80px 140px 100px 1fr 140px 140px 100px;";
</script>

<div class="pt-2 h-full flex flex-col min-h-0">
  <div class="border-2 border-black rounded-base bg-white flex flex-col h-full max-h-[500px] overflow-hidden">

    <div class="overflow-auto flex-1 w-full relative">
      {#if records.length === 0}
        <div class="flex items-center justify-center p-8 bg-white h-full">
          <p class="text-sm font-bold text-black/50">No evaluation records to display</p>
        </div>
      {:else}
        <div class="min-w-[1050px] w-full">

          <!-- Sticky header -->
          <div class="bg-white border-b-2 border-black sticky top-0 z-5 w-full">
            <div class="grid gap-3 text-black text-xs font-bold px-4 py-3 items-center" style={gridLayout}>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Prompt</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">ID</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Created</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Status</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Entity Type</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Processing Started</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Processing Ended</span></div>
              <div class="text-center"><span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 border border-transparent">Duration</span></div>
            </div>
          </div>

          <!-- Rows -->
          <div class="bg-white w-full">
            {#each records as record, i}
              <button
                class="grid gap-3 items-center w-full px-4 py-3 border-b border-gray-200 transition-colors {i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-primary-100 cursor-pointer text-left group"
                style={gridLayout}
                onclick={() => selectRecord(record)}
              >
                <!-- Prompt name -->
                <div class="flex justify-center">
                  <span class="px-2 py-0.5 rounded-base border border-black bg-primary-100 text-primary-950
                               text-xss font-black uppercase tracking-wider truncate max-w-[128px]"
                        title={record._agentName}>
                    {record._agentName}
                  </span>
                </div>

                <!-- UID -->
                <div class="text-center">
                  <span class="text-xs font-mono text-gray-600 group-hover:text-black font-bold">{record.uid.slice(0, 8)}</span>
                </div>

                <!-- Created -->
                <div class="flex items-center justify-center gap-2 min-w-0">
                  <div class={`w-1.5 h-4 rounded-sm flex-shrink-0 ${statusBar(record.status)}`}></div>
                  <span class="text-xs text-black font-mono truncate">{fmt(record.created_at)}</span>
                </div>

                <!-- Status badge -->
                <div class="flex justify-center">
                  <span class="px-2 py-1 rounded border-1 text-xs font-bold {statusBadge(record.status)}">
                    {record.status.toUpperCase()}
                  </span>
                </div>

                <!-- Entity type -->
                <div class="text-center">
                  <span class="px-2 py-1 rounded border-1 bg-primary-100 border-primary-900 text-primary-900 text-xs font-bold">
                    {record.entity_type}
                  </span>
                </div>

                <!-- Processing started -->
                <div class="text-center">
                  <span class="text-xs font-mono text-gray-600">
                    {record.processing_started_at ? fmt(record.processing_started_at) : 'N/A'}
                  </span>
                </div>

                <!-- Processing ended -->
                <div class="text-center">
                  <span class="text-xs font-mono text-gray-600">
                    {record.processing_ended_at ? fmt(record.processing_ended_at) : 'N/A'}
                  </span>
                </div>

                <!-- Duration -->
                <div class="text-center">
                  <span class="text-xs font-medium text-gray-700">
                    {fmtDur(record.processing_duration)}
                  </span>
                </div>
              </button>
            {/each}
          </div>

        </div>
      {/if}
    </div>

    <!-- Pagination footer -->
    {#if records.length > 0}
      <div class="border-t-2 border-black bg-gray-50 p-2 flex justify-center gap-2 items-center">
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0 disabled:hover:shadow-small"
          onclick={() => onPageChange('previous')}
          disabled={!hasPrevious}
        >
          <ArrowLeft class="w-4 h-4" color="currentColor"/>
        </button>
        <button
          class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9 px-3 flex items-center justify-center disabled:opacity-50 disabled:hover:translate-x-0 disabled:hover:translate-y-0 disabled:hover:shadow-small"
          onclick={() => onPageChange('next')}
          disabled={!hasNext}
        >
          <ArrowRight class="w-4 h-4" color="currentColor"/>
        </button>
      </div>
    {/if}

  </div>

  {#if selectedRecord && isSelected}
    <EvalRecordSideBar
      selectedRecord={selectedRecord}
      onClose={handleClosePanel}
    />
  {/if}
</div>
