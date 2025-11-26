<script lang="ts">
  import type { TraceListItem } from "./types";
  import { formatDuration, formatTimestamp } from "./utils";

  /**
   * Individual trace table row component for virtual rendering.
   * Optimized for performance with minimal reactivity.
   */

  let { trace, index, onclick }: {
    trace: TraceListItem;
    index: number;
    onclick?: (trace: TraceListItem) => void;
  } = $props();

  function getStatusColor(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) return 'bg-secondary-500';
    if (statusCode >= 400 && statusCode < 500) return 'bg-warning-500';
    if (statusCode >= 500) return 'bg-error-600';
    return 'bg-gray-400';
  }

  function handleClick() {
    onclick?.(trace);
  }
</script>

<tr
  class={`border-b border-gray-200 hover:bg-primary-200 cursor-pointer transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
  onclick={handleClick}
  role="button"
  tabindex="0"
>

  <td class="p-2 text-center">
    <span class="text-xs font-mono text-gray-500">#{index + 1}</span>
  </td>

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
    <span class={`inline-block px-2 py-1 rounded text-white text-xs font-bold ${getStatusColor(trace.status_code)}`}>
      {trace.status_code}
    </span>
  </td>
</tr>