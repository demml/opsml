<script lang="ts">
  import type { TraceListItem } from "./types";
  import { formatDuration, formatTimestamp } from "./utils";

  let { traces } = $props<{
    traces: TraceListItem[];
  }>();

  type SortField = 'date' | 'service' | 'operation' | 'duration' | 'spans' | 'status';
  type SortDirection = 'asc' | 'desc';

  let sortField = $state<SortField>('date');
  let sortDirection = $state<SortDirection>('desc');

  /**
   * Sort traces based on current sort configuration
   */
  const sortedTraces = $derived.by(() => {
    const sorted = [...traces].sort((a, b) => {
      let compareResult = 0;

      switch (sortField) {
        case 'date':
          compareResult = new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
          break;
        case 'service':
          compareResult = (a.service_name ?? '').localeCompare(b.service_name ?? '');
          break;
        case 'operation':
          compareResult = (a.root_operation ?? '').localeCompare(b.root_operation ?? '');
          break;
        case 'duration':
          compareResult = (a.duration_ms ?? 0) - (b.duration_ms ?? 0);
          break;
        case 'spans':
          compareResult = (a.span_count ?? 0) - (b.span_count ?? 0);
          break;
        case 'status':
          compareResult = (a.has_errors ? 1 : 0) - (b.has_errors ? 1 : 0);
          break;
      }

      return sortDirection === 'asc' ? compareResult : -compareResult;
    });

    return sorted;
  });

  /**
   * Toggle sort direction or change sort field
   */
  function handleSort(field: SortField) {
    if (sortField === field) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortField = field;
      sortDirection = 'desc';
    }
  }

  /**
   * Get sort indicator icon
   */
  function getSortIcon(field: SortField): string {
    if (sortField !== field) return '↕️';
    return sortDirection === 'asc' ? '↑' : '↓';
  }

  /**
   * Handle row click for future span detail view
   */
  function handleRowClick(trace: TraceListItem) {
    // TODO: Open side panel with span details
    console.log('Clicked trace:', trace.trace_id);
  }

  /**
   * Get HTTP status code from trace
   */
  function getStatusCode(trace: TraceListItem): number {
    return trace.status_code;
  }

  /**
   * Get status badge color based on status code
   */
  function getStatusColor(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) {
      return 'bg-secondary-500';
    } else if (statusCode >= 400 && statusCode < 500) {
      return 'bg-warning-500';
    } else if (statusCode >= 500) {
      return 'bg-error-600';
    }
    return 'bg-gray-400';
  }
</script>

<div class="flex flex-col">
  <div class="items-center mr-2 font-bold text-primary-800 text-lg">Traces</div>
  <div class="overflow-auto w-full border-2 border-black rounded-lg">
    <table class="text-black border-collapse text-sm bg-white w-full">
      <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
        <tr>

          <th class="p-2 font-heading text-left">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1"
              onclick={() => handleSort('date')}
            >
              <span>DATE</span>
              <span class="text-xs">{getSortIcon('date')}</span>
            </button>
          </th>


          <th class="p-2 font-heading text-left">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1"
              onclick={() => handleSort('service')}
            >
              <span>SERVICE</span>
              <span class="text-xs">{getSortIcon('service')}</span>
            </button>
          </th>


          <th class="p-2 font-heading text-left">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1"
              onclick={() => handleSort('operation')}
            >
              <span>RESOURCE</span>
              <span class="text-xs">{getSortIcon('operation')}</span>
            </button>
          </th>


          <th class="p-2 font-heading text-center">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1 mx-auto"
              onclick={() => handleSort('duration')}
            >
              <span>DURATION</span>
              <span class="text-xs">{getSortIcon('duration')}</span>
            </button>
          </th>


          <th class="p-2 font-heading text-center">
            <span class="px-2 py-1 rounded-full bg-primary-100 text-primary-800">METHOD</span>
          </th>

          <th class="p-2 font-heading text-center">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1 mx-auto"
              onclick={() => handleSort('spans')}
            >
              <span>SPANS</span>
              <span class="text-xs">{getSortIcon('spans')}</span>
            </button>
          </th>


          <th class="p-2 font-heading text-center">
            <button
              class="px-2 py-1 rounded-full bg-primary-100 text-primary-800 hover:bg-primary-200 transition-colors flex items-center gap-1 mx-auto"
              onclick={() => handleSort('status')}
            >
              <span>STATUS CODE</span>
              <span class="text-xs">{getSortIcon('status')}</span>
            </button>
          </th>
        </tr>
      </thead>
      <tbody>
      {#each sortedTraces as trace, i}
        <tr
          class={`border-b border-gray-200 hover:bg-primary-200 cursor-pointer transition-colors ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
          onclick={() => handleRowClick(trace)}
        >

          <td class="p-2 text-left">
            <div class="flex items-center gap-2">
              <div class={`w-1.5 h-4 rounded-sm ${trace.has_errors ? 'bg-error-600' : 'bg-secondary-500'}`}></div>
              <span class="text-xs font-mono">{formatTimestamp(trace.start_time)}</span>
            </div>
          </td>


          <td class="p-2 text-left">
            <div class="flex items-center gap-2">
              <span class="inline-block w-2 h-2 rounded-full bg-primary-500"></span>
              <span class="font-medium">{trace.service_name ?? 'Unknown'}</span>
            </div>
          </td>


          <td class="p-2 text-left">
            <span class="text-gray-700">{trace.root_operation ?? 'N/A'}</span>
          </td>


          <td class="p-2 text-center">
            <span class="text-xs font-mono">{formatDuration(trace.duration_ms)}</span>
          </td>

          <td class="p-2 text-center">
            <span class="px-2 py-1 rounded bg-gray-100 text-gray-800 text-xs font-medium">
              {trace.scope ?? 'GET'}
            </span>
          </td>

          <td class="p-2 text-center">
            <span class="text-xs font-medium">{trace.span_count ?? 0}</span>
          </td>

          <td class="p-2 text-center">
            <span class={`inline-block px-2 py-1 rounded text-white text-xs font-bold ${getStatusColor(getStatusCode(trace))}`}>
              {getStatusCode(trace)}
            </span>
          </td>
        </tr>
      {/each}
      </tbody>
    </table>
  </div>

  {#if sortedTraces.length === 0}
    <div class="text-center py-8 text-gray-500">
      No traces found
    </div>
  {/if}
</div>