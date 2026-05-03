<script lang="ts">
  import { Users } from 'lucide-svelte';
  import type { GenAiAgentActivity } from './types';
  import { fmtCompact } from './format';

  let { agents }: { agents: GenAiAgentActivity[] } = $props();

  type SortCol = 'agent_name' | 'span_count' | 'total_input_tokens' | 'total_output_tokens';
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

  const sorted = $derived([...agents].sort((a, b) => {
    const av = (a[sortCol] ?? 0) as string | number;
    const bv = (b[sortCol] ?? 0) as string | number;
    const cmp = av < bv ? -1 : av > bv ? 1 : 0;
    return sortAsc ? cmp : -cmp;
  }));
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">
  <div class="px-3 py-1.5 border-b-2 border-black bg-surface-100 flex items-center gap-1.5">
    <Users class="w-3 h-3 text-primary-700" />
    <span class="text-xs font-black uppercase tracking-wide text-primary-800">Agents</span>
  </div>
  <div class="overflow-x-auto">
    <table class="w-full text-xs">
      <thead>
        <tr class="bg-surface-100 border-b-2 border-black">
          <th class="px-2 py-1 text-left text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('agent_name')} class="hover:text-primary-950">
              Agent {sortCol === 'agent_name' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('span_count')} class="hover:text-primary-950">
              Spans {sortCol === 'span_count' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('total_input_tokens')} class="hover:text-primary-950">
              In {sortCol === 'total_input_tokens' ? (sortAsc ? '▲' : '▼') : ''}
            </button>
          </th>
          <th class="px-2 py-1 text-right text-xs font-black uppercase text-primary-700">
            <button onclick={() => toggle('total_output_tokens')} class="hover:text-primary-950">
              Out {sortCol === 'total_output_tokens' ? (sortAsc ? '▲' : '▼') : ''}
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
          {#each sorted as row (row.agent_id ?? row.agent_name)}
            <tr class="border-b border-black hover:bg-primary-100">
              <td class="px-2 py-1 text-xs font-mono text-primary-900 truncate max-w-[120px]">{row.agent_name ?? '—'}</td>
              <td class="px-2 py-1 text-xs font-mono text-primary-900 text-right">{fmtCompact(row.span_count)}</td>
              <td class="px-2 py-1 text-xs font-mono text-primary-900 text-right">{fmtCompact(row.total_input_tokens)}</td>
              <td class="px-2 py-1 text-xs font-mono text-primary-900 text-right">{fmtCompact(row.total_output_tokens)}</td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>
