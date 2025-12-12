<script lang="ts">
  import type { TraceSpan } from './types';
  import { formatDuration, hasSpanError } from './utils';
  import { CircleX, Clock } from 'lucide-svelte';

  let {
    spans,
    totalDuration,
    selectedSpan,
    onSpanSelect,
    slowestSpan,
  }: {
    spans: TraceSpan[];
    totalDuration: number;
    selectedSpan: TraceSpan | null;
    onSpanSelect: (span: TraceSpan) => void;
    slowestSpan?: TraceSpan | null;
  } = $props();

  const ROW_HEIGHT = 28;
  const INDENT_PX = 16;

  /** Returns badge classes based on structured coloring rules */
  function getServiceBadgeClasses(span: TraceSpan): string {
    // Root span (depth 0) → tertiary
    if (span.depth === 0) {
      return 'border-tertiary-950 bg-tertiary-100 text-tertiary-950';
    }

    if (slowestSpan && span.span_id === slowestSpan.span_id) {
      return 'warn-color';
    }

    if (hasSpanError(span)) {
      return 'border-error-800 bg-error-100 text-error-800';
    }

    return 'border-secondary-950 bg-secondary-100 text-secondary-950';
  }


  function getSpanPosition(span: TraceSpan): { left: number; width: number } {
    const spanStart = new Date(span.start_time).getTime();
    const traceStart = new Date(spans[0].start_time).getTime();
    const offset = spanStart - traceStart;
    const duration = span.duration_ms || 0;

    return {
      left: (offset / totalDuration) * 100,
      width: Math.max((duration / totalDuration) * 100, 0.2),
    };
  }

  const sortedSpans = $derived(
  [...spans].sort((a, b) => {
    // Primary sort: start time (chronological order)
    const timeA = new Date(a.start_time).getTime();
    const timeB = new Date(b.start_time).getTime();
    if (timeA !== timeB) return timeA - timeB;

    // Secondary sort: depth (parent before child at same time)
    if (a.depth !== b.depth) return a.depth - b.depth;

    // Tertiary sort: span_order as tiebreaker
    return a.span_order - b.span_order;
  })
);
</script>

<div class="flex flex-col h-full bg-white text-sm overflow-hidden">
  <!-- Timeline Header -->
  <div class="sticky top-0 z-20 bg-surface-50 border-b border-gray-300 flex-shrink-0">
    <div class="flex">
      <!-- Service name column spacer -->
      <div class="w-[35%] min-w-[280px] border-r border-gray-300"></div>

      <!-- Timeline marks -->
      <div class="flex-1 relative h-8 px-2">
        {#each [0, 0.25, 0.5, 0.75, 1.0] as mark, i}
          <div
            class="absolute top-0 bottom-0 flex flex-col {i === 0 ? 'items-start' : i === 4 ? 'items-end' : 'items-center'}"
            style="left: {mark * 100}%"
          >
            <div class="flex-1 border-l border-gray-300"></div>
            <span class="text-xs text-gray-500 font-mono mt-1 {i !== 0 && i !== 4 ? '-translate-x-1/2' : ''}">
              {formatDuration(totalDuration * mark)}
            </span>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Span List -->
  <div class="flex-1 overflow-auto">
    {#each sortedSpans as span (span.span_id)}
      {@const position = getSpanPosition(span)}
      {@const isSelected = selectedSpan?.span_id === span.span_id}
      {@const indent = span.depth * INDENT_PX}
      {@const serviceName = span.service_name}
      {@const spanHasError = hasSpanError(span)}
      {@const badgeClasses = getServiceBadgeClasses(span)}
      {@const isSlowestSpan = slowestSpan && span.span_id === slowestSpan.span_id}

      <div
        class="flex group cursor-pointer hover:bg-surface-600 border-b border-gray-100 transition-colors"
        style="height: {ROW_HEIGHT}px"
        class:bg-primary-50={isSelected}
        onclick={() => onSpanSelect(span)}
        onkeydown={(e) => e.key === 'Enter' && onSpanSelect(span)}
        role="button"
        tabindex="0"
      >
        <!-- Left: Service & Operation Name -->
        <div
          class="w-[35%] min-w-[280px] flex items-center gap-1.5 px-2 border-r border-gray-100 overflow-hidden flex-shrink-0"
          style="padding-left: calc({indent}px + 0.5rem);"
        >

          {#if span.depth > 0}
            <span class="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-primary-100 border-primary-950, border-1 text-primary-950 rounded text-xs font-bold">
              {span.depth}
            </span>
          {/if}

          <span class="border px-1.5 py-0.5 text-xs rounded flex-shrink-0 {badgeClasses}">
            {serviceName}
          </span>

          {#if isSlowestSpan}
            <Clock class="w-4 h-4 text-retro-orange-900 flex-shrink-0"/>
          {/if}

          {#if spanHasError}
            <CircleX class="w-4 h-4 text-error-600 flex-shrink-0"/>
          {/if}

          <span class="text-xs truncate font-medium text-gray-900 flex-1 min-w-0" title={span.span_name}>
            {span.span_name}
          </span>
        </div>

        <div class="flex-1 flex items-center gap-2 px-2 min-w-0">
          <div class="relative flex-1 h-5 min-w-0">
            <!-- Span bar -->
            <div
              class="absolute h-full rounded border border-black transition-all"
              class:border-2={isSelected}
              class:shadow-small={isSelected}
              class:bg-error-200={spanHasError}
              class:bg-secondary-200={!spanHasError}
              class:opacity-60={!isSelected && selectedSpan !== null}
              style="left: {position.left}%; width: {position.width}%;"
            >
              <!-- Duration label inside bar if wide enough -->
              {#if position.width > 18}
                <span
                  class="absolute inset-0 flex items-center justify-center text-xs overflow-hidden"
                  class:text-error-800={spanHasError}
                  class:text-secondary-950={!spanHasError}
                >
                  {formatDuration(span.duration_ms)}
                </span>
              {/if}
            </div>
          </div>

          <!-- Duration on right side - now in separate fixed-width container -->
          <span class="w-16 text-xs font-mono text-gray-600 text-right flex-shrink-0 whitespace-nowrap">
            {formatDuration(span.duration_ms)}
          </span>
        </div>
      </div>
    {/each}
  </div>
</div>