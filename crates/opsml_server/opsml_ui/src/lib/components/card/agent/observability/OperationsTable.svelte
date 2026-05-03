<script lang="ts">
  import type { GenAiOperationBreakdown } from './types';
  import { fmtCompact, fmtMs, fmtPct } from './format';

  let { operations }: { operations: GenAiOperationBreakdown[] } = $props();

  type SortCol = 'operation_name' | 'span_count' | 'avg_duration_ms' | 'error_rate';
  let sortCol = $state<SortCol>('span_count');
  let sortAsc = $state(false);

  function toggle(col: SortCol) {
    if (sortCol === col) {
      sortAsc = !sortAsc;
    } else {
      sortCol = col;
      sortAsc = false;
    }
  }

  const sorted = $derived([...operations].sort((a, b) => {
    const av = (a[sortCol] ?? 0) as string | number;
    const bv = (b[sortCol] ?? 0) as string | number;
    const cmp = av < bv ? -1 : av > bv ? 1 : 0;
    return sortAsc ? cmp : -cmp;
  }));
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
  <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100">
    <span class="text-xs font-black uppercase tracking-wide text-primary-800">Operations</span>
  </div>
  <div class="overflow-x-auto">
    <table class="w-full text-xs">
      <thead>
        <tr class="bg-surface-100 border-b-2 border-black">
          <th class="px-2 py-1 text-left text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('operation_name')} class="hover:text-primary-950">
              Operation {sortCol === 'operation_name' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('span_count')} class="hover:text-primary-950">
              Spans {sortCol === 'span_count' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('avg_duration_ms')} class="hover:text-primary-950">
              Avg {sortCol === 'avg_duration_ms' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('error_rate')} class="hover:text-primary-950">
              Err {sortCol === 'error_rate' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
        </tr>
      </thead>
      <tbody>
        {#if sorted.length === 0}
          <tr>
            <td colspan="4" class="px-2 py-3 text-center text-xs text-primary-700">No data</td>
          </tr>
        {:else}
          {#each sorted as row (row.operation_name)}
            <tr class="border-b border-black hover:bg-primary-100">
              <td class="px-2 py-1 text-xs font-mono text-primary-900 truncate max-w-[140px]">{row.operation_name}</td>
              <td class="px-2 py-1 text-xs font-mono text-primary-900 text-right">{fmtCompact(row.span_count)}</td>
              <td class="px-2 py-1 text-xs font-mono text-primary-900 text-right">{fmtMs(row.avg_duration_ms)}</td>
              <td class="px-2 py-1 text-xs font-mono text-right {row.error_rate > 0.02 ? 'text-error-700 font-bold' : 'text-primary-900'}">{fmtPct(row.error_rate)}</td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
