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

  /**
   * Build a map of parent_span_id -> array of child spans for efficient lookup
   */
  function buildParentChildMap(allSpans: TraceSpan[]): Map<string, TraceSpan[]> {
    const map = new Map<string, TraceSpan[]>();

    for (const span of allSpans) {
      if (span.parent_span_id) {
        const existing = map.get(span.parent_span_id) || [];
        existing.push(span);
        map.set(span.parent_span_id, existing);
      }
    }

    return map;
  }

  /**
   * Get all descendants of a span recursively
   */
  function getAllDescendants(
    spanId: string,
    parentChildMap: Map<string, TraceSpan[]>
  ): TraceSpan[] {
    const children = parentChildMap.get(spanId) || [];
    const descendants: TraceSpan[] = [...children];

    for (const child of children) {
      descendants.push(...getAllDescendants(child.span_id, parentChildMap));
    }

    return descendants;
  }

  /**
   * Determines if this span is the last child among its siblings
   */
  function isLastSibling(
    span: TraceSpan,
    allSpans: TraceSpan[],
    parentChildMap: Map<string, TraceSpan[]>
  ): boolean {
    if (!span.parent_span_id) return true;

    const siblings = parentChildMap.get(span.parent_span_id) || [];
    if (siblings.length === 0) return true;

    const siblingIndices = siblings.map(s => allSpans.findIndex(sp => sp.span_id === s.span_id));
    const currentIndex = allSpans.findIndex(s => s.span_id === span.span_id);

    return Math.max(...siblingIndices) === currentIndex;
  }

  /**
   * For a given span and ancestor depth, determine if a vertical line should be drawn.
   * A line should be drawn if ANY descendant of the ancestor at that depth appears
   * AFTER the current span in the sorted list.
   */
  function shouldDrawVerticalLine(
  span: TraceSpan,
  depth: number,
  allSpans: TraceSpan[],
  parentChildMap: Map<string, TraceSpan[]>
): boolean {
  if (depth >= span.depth) return false;

  let ancestor: TraceSpan | undefined = span;
  while (ancestor && ancestor.depth > depth) {
    ancestor = allSpans.find(s => s.span_id === ancestor!.parent_span_id);
  }

  if (!ancestor || ancestor.depth !== depth) return false;
  if (!ancestor.parent_span_id) return false;

  const siblings = parentChildMap.get(ancestor.parent_span_id) || [];
  const currentIndex = allSpans.findIndex(s => s.span_id === span.span_id);

  for (const sibling of siblings) {
    const siblingIndex = allSpans.findIndex(s => s.span_id === sibling.span_id);
    if (siblingIndex > currentIndex) return true;

    const siblingDescendants = getAllDescendants(sibling.span_id, parentChildMap);
    const descendantIndices = siblingDescendants.map(d =>
      allSpans.findIndex(s => s.span_id === d.span_id)
    );

    if (descendantIndices.some(idx => idx > currentIndex)) return true;
  }

  return false;
}

    /**
   * Sorts spans using depth-first traversal to maintain parent-child hierarchy
   * while respecting chronological order within sibling groups.
   */
  function sortSpansDepthFirst(spans: TraceSpan[]): TraceSpan[] {

    const childrenMap = new Map<string | null, TraceSpan[]>();

    for (const span of spans) {
      const parentId = span.parent_span_id || null;
      if (!childrenMap.has(parentId)) {
        childrenMap.set(parentId, []);
      }
      childrenMap.get(parentId)!.push(span);
    }

    for (const siblings of childrenMap.values()) {
      siblings.sort((a, b) => {
        const timeA = new Date(a.start_time).getTime();
        const timeB = new Date(b.start_time).getTime();
        if (timeA !== timeB) return timeA - timeB;
        return a.span_order - b.span_order;
      });
    }

    const result: TraceSpan[] = [];

    function traverse(parentId: string | null) {
      const children = childrenMap.get(parentId) || [];
      for (const child of children) {
        result.push(child);
        traverse(child.span_id);
      }
    }

    traverse(null);

    return result;
  }

  const sortedSpans = $derived(sortSpansDepthFirst(spans));

  const parentChildMap = $derived(buildParentChildMap(sortedSpans));
</script>

<div class="flex flex-col h-full bg-white text-sm overflow-hidden">
  <!-- Timeline Header -->
  <div class="sticky top-0 bg-surface-50 border-b border-gray-300 flex-shrink-0">
    <div class="flex">
      <div class="w-[35%] min-w-[280px] border-r border-gray-300"></div>
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
  <div class="flex-1 overflow-auto pb-6">
    {#each sortedSpans as span (span.span_id)}
      {@const position = getSpanPosition(span)}
      {@const isSelected = selectedSpan?.span_id === span.span_id}
      {@const indent = span.depth * INDENT_PX}
      {@const serviceName = span.service_name}
      {@const spanHasError = hasSpanError(span)}
      {@const badgeClasses = getServiceBadgeClasses(span)}
      {@const isSlowestSpan = slowestSpan && span.span_id === slowestSpan.span_id}
      {@const isLast = isLastSibling(span, sortedSpans, parentChildMap)}

      <div
          class="flex group cursor-pointer hover:bg-surface-600 transition-colors"
          style="height: {ROW_HEIGHT}px"
          class:bg-primary-50={isSelected}
          onclick={() => onSpanSelect(span)}
          onkeydown={(e) => e.key === 'Enter' && onSpanSelect(span)}
          role="button"
          tabindex="0"
        >

        <div
            class="w-[35%] min-w-[280px] flex items-center gap-1.5 px-2 border-r border-gray-100 overflow-hidden flex-shrink-0 relative"
            style="padding-left: calc({indent}px + 0.5rem);"
          >

          {#if span.depth > 0}
            {#each Array.from({ length: span.depth }) as _, depthIndex}
              {@const shouldDrawLine = shouldDrawVerticalLine(span, depthIndex, sortedSpans, parentChildMap)}
              {@const isCurrentLevel = depthIndex === span.depth - 1}
              {@const lineLeftPosition = depthIndex * INDENT_PX + 8}

              <div
                class="absolute pointer-events-none"
                style="left: calc({lineLeftPosition}px + 0.5rem); width: 1px; top: 0; height: {ROW_HEIGHT}px;"
              >
                {#if isCurrentLevel}
                  <!-- L-shape or T-shape connector at current depth -->
                  <div class="relative w-full h-full">
                    <!-- Vertical line from top to middle -->
                    <div class="absolute top-0 left-0 w-full bg-gray-400" style="height: {ROW_HEIGHT / 2}px;"></div>

                    <!-- Horizontal line extending to the right -->
                    <div
                      class="absolute left-0 bg-gray-400"
                      style="top: {ROW_HEIGHT / 2}px; height: 1px; width: {INDENT_PX / 2}px;"
                    ></div>

                    {#if !isLast}
                      <div class="absolute left-0 w-full bg-gray-400" style="top: {ROW_HEIGHT / 2}px; height: {ROW_HEIGHT / 2}px;"></div>
                    {:else if span.parent_span_id}
                      {@const parent = sortedSpans.find(s => s.span_id === span.parent_span_id)}
                      {#if parent && !isLastSibling(parent, sortedSpans, parentChildMap)}
                        <div class="absolute left-0 w-full bg-gray-400" style="top: {ROW_HEIGHT / 2}px; height: {ROW_HEIGHT / 2}px;"></div>
                      {/if}
                    {/if}
                  </div>
                {:else if shouldDrawLine}
                  <div class="w-full bg-gray-400" style="height: {ROW_HEIGHT}px;"></div>
                {/if}
              </div>
            {/each}
          {/if}

          {#if span.depth > 0}
            <span class="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-primary-100 border-primary-950 border-1 text-primary-950 rounded text-xs font-bold">
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
            <div
              class="absolute h-full rounded border border-black transition-all"
              class:border-2={isSelected}
              class:shadow-small={isSelected}
              class:bg-error-200={spanHasError}
              class:bg-secondary-200={!spanHasError}
              class:opacity-60={!isSelected && selectedSpan !== null}
              style="left: {position.left}%; width: {position.width}%;"
            >
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

          <span class="w-16 text-xs font-mono text-gray-600 text-right flex-shrink-0 whitespace-nowrap">
            {formatDuration(span.duration_ms)}
          </span>
        </div>
      </div>
    {/each}
  </div>
</div>