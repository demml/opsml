<script lang="ts">
  import type { TraceSpan } from './types';
  import { formatDuration, hasSpanError } from './utils';
  import { CircleX, Clock, Timer } from 'lucide-svelte';

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

  const ROW_HEIGHT = 32;
  const INDENT_PX = 14;

  function getServiceBadgeClasses(span: TraceSpan): string {
    if (span.depth === 0) {
      return 'border-primary-950 bg-primary-100 text-black';
    }
    if (slowestSpan && span.span_id === slowestSpan.span_id) {
      return 'warn-color';
    }
    if (hasSpanError(span)) {
      return 'border-error-800 bg-error-100 text-error-800';
    }
    return 'border-secondary-950 bg-secondary-100 text-black';
  }

  function getSpanBarClasses(span: TraceSpan, isSelected: boolean): string {
    const base = 'absolute h-full border transition-all duration-150';
    if (hasSpanError(span)) {
      return `${base} bg-error-200 border-error-700 ${isSelected ? 'border-1 shadow-small' : 'border'}`;
    }
    return `${base} bg-secondary-200 border-secondary-700 ${isSelected ? 'border-1 shadow-small' : 'border'}`;
  }

  function getSpanPosition(span: TraceSpan): { left: number; width: number } {
    const spanStart = new Date(span.start_time).getTime();
    const traceStart = new Date(spans[0].start_time).getTime();
    const offset = spanStart - traceStart;
    const duration = span.duration_ms || 0;

    return {
      left: (offset / totalDuration) * 100,
      width: Math.max((duration / totalDuration) * 100, 0.3),
    };
  }

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

  <!-- Column Headers -->
  <div class="sticky top-0 z-10 flex-shrink-0 bg-surface-50 border-b-2 border-black">
    <div class="flex">
      <!-- Left column label -->
      <div class="w-[38%] min-w-[260px] flex items-center px-3 py-1.5 border-r-1 border-black">
        <span class="text-xs font-black uppercase tracking-widest text-black">Span</span>
      </div>
      <!-- Timeline marks -->
      <div class="flex-1 relative h-8 flex items-end px-1 pb-1">
        {#each [0, 0.25, 0.5, 0.75, 1.0] as mark, i}
          <div
            class="absolute top-0 bottom-0 flex flex-col justify-end {i === 0 ? 'items-start' : i === 4 ? 'items-end' : 'items-center'}"
            style="left: {mark * 100}%"
          >
            <div class="w-px flex-1 {i === 0 ? '' : 'bg-gray-300'}"></div>
            <span class="text-xs font-mono text-gray-500 leading-none {i !== 0 && i !== 4 ? '-translate-x-1/2' : i === 4 ? '-translate-x-full' : ''}">
              {formatDuration(totalDuration * mark)}
            </span>
          </div>
        {/each}
        <div class="flex items-center gap-1 absolute top-1 right-1">
          <Timer class="w-3 h-3 text-gray-400" />
          <span class="text-xs font-black uppercase tracking-widest text-black">Timeline</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Span Rows -->
  <div class="flex-1 overflow-auto">
    {#each sortedSpans as span (span.span_id)}
      {@const position = getSpanPosition(span)}
      {@const isSelected = selectedSpan?.span_id === span.span_id}
      {@const indent = span.depth * INDENT_PX}
      {@const spanHasError = hasSpanError(span)}
      {@const badgeClasses = getServiceBadgeClasses(span)}
      {@const isSlowestSpan = slowestSpan && span.span_id === slowestSpan.span_id}
      {@const isLast = isLastSibling(span, sortedSpans, parentChildMap)}

      <div
        class="flex group cursor-pointer transition-colors border-b border-gray-100
          {isSelected
            ? 'bg-primary-50 border-l-4 border-l-primary-500'
            : 'hover:bg-surface-200 border-l-4 border-l-transparent'}"
        style="height: {ROW_HEIGHT}px"
        onclick={() => onSpanSelect(span)}
        onkeydown={(e) => e.key === 'Enter' && onSpanSelect(span)}
        role="button"
        tabindex="0"
      >

        <!-- Left column: name and badges -->
        <div
          class="w-[38%] min-w-[260px] flex items-center gap-1.5 px-2 border-r border-gray-200 overflow-hidden flex-shrink-0 relative"
          style="padding-left: calc({indent}px + 0.5rem);"
        >
          <!-- Tree connector lines -->
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
                  <div class="relative w-full h-full">
                    <div class="absolute top-0 left-0 w-full bg-gray-300" style="height: {ROW_HEIGHT / 2}px;"></div>
                    <div class="absolute left-0 bg-gray-300" style="top: {ROW_HEIGHT / 2}px; height: 1px; width: {INDENT_PX / 2}px;"></div>
                    {#if !isLast}
                      <div class="absolute left-0 w-full bg-gray-300" style="top: {ROW_HEIGHT / 2}px; height: {ROW_HEIGHT / 2}px;"></div>
                    {:else if span.parent_span_id}
                      {@const parent = sortedSpans.find(s => s.span_id === span.parent_span_id)}
                      {#if parent && !isLastSibling(parent, sortedSpans, parentChildMap)}
                        <div class="absolute left-0 w-full bg-gray-300" style="top: {ROW_HEIGHT / 2}px; height: {ROW_HEIGHT / 2}px;"></div>
                      {/if}
                    {/if}
                  </div>
                {:else if shouldDrawLine}
                  <div class="w-full bg-gray-300" style="height: {ROW_HEIGHT}px;"></div>
                {/if}
              </div>
            {/each}
          {/if}

          <!-- Depth pill (children only) -->
          {#if span.depth > 0}
            <span class="z-10 flex-shrink-0 w-4 h-4 flex items-center justify-center bg-surface-100 border border-primary-950 text-primary-950 rounded text-xs font-black leading-none">
              {span.depth}
            </span>
          {/if}

          <!-- Span name badge -->
          <span class="border px-1.5 py-0.5 text-xs flex-shrink-0 max-w-[200px] truncate {badgeClasses}">
            {span.span_name}
          </span>

          <!-- Slow indicator -->
          {#if isSlowestSpan}
            <Clock class="w-3.5 h-3.5 text-retro-orange-900 flex-shrink-0" />
          {/if}

          <!-- Error indicator -->
          {#if spanHasError}
            <CircleX class="w-3.5 h-3.5 text-error-600 flex-shrink-0" />
          {/if}
        </div>

        <!-- Right column: timeline bar + duration -->
        <div class="flex-1 flex items-center gap-2 px-2 min-w-0">
          <div class="relative flex-1 h-[18px] min-w-0">
            <div
              class={getSpanBarClasses(span, isSelected)}
              style="left: {position.left}%; width: {position.width}%;"
            >
              {#if position.width > 16}
                <span
                  class="absolute inset-0 flex items-center justify-center text-xs font-mono overflow-hidden px-1"
                  class:text-error-800={spanHasError}
                  class:text-secondary-950={!spanHasError}
                >
                  {formatDuration(span.duration_ms)}
                </span>
              {/if}
            </div>
          </div>
          <span class="w-14 text-xs font-mono text-gray-600 text-right flex-shrink-0 whitespace-nowrap">
            {formatDuration(span.duration_ms)}
          </span>
        </div>

      </div>
    {/each}
  </div>

</div>
