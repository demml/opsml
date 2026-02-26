<script lang="ts">
  import type { TraceSpan } from './types';
  import { formatDuration, hasSpanError } from './utils';
  import { CircleX, Clock, ChevronRight } from 'lucide-svelte';

  // Scroll-sync refs
  let spanScrollContainer: HTMLDivElement;
  let timelineScrollContainer: HTMLDivElement;
  let isSpanScrolling = false;
  let isTimelineScrolling = false;
  let hoverX = $state<number | null>(null); // cursor X as percentage within timeline column

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

  const ROW_HEIGHT = 34;
  const INDENT_PX = 14;
  // Axis tick marks at 0%, 25%, 50%, 75%, 100%
  const AXIS_MARKS = [0, 0.25, 0.5, 0.75, 1.0];

  // ─── Span type classification ────────────────────────────────────────────

  type SpanType = 'root' | 'llm' | 'tool' | 'error' | 'slow' | 'default';

  function getSpanType(span: TraceSpan): SpanType {
    if (span.depth === 0) return 'root';
    if (hasSpanError(span)) return 'error';
    if (slowestSpan && span.span_id === slowestSpan.span_id) return 'slow';
    const name = (span.span_name || '').toLowerCase();
    const kind = (span.span_kind || '').toLowerCase();
    if (name.includes('llm') || name.includes('completion') || name.includes('chat') || kind === 'client') return 'llm';
    if (name.includes('tool') || name.includes('function') || name.includes('call')) return 'tool';
    return 'default';
  }

  // Color squares for span type
  function getTypeColor(type: SpanType): string {
    switch (type) {
      case 'root':    return 'bg-primary-500 border-primary-800';
      case 'llm':     return 'bg-secondary-400 border-secondary-700';
      case 'tool':    return 'bg-retro-orange-400 border-retro-orange-700';
      case 'error':   return 'bg-error-500 border-error-800';
      case 'slow':    return 'bg-warning-400 border-warning-700';
      default:        return 'bg-gray-300 border-gray-600';
    }
  }

  function getBarColor(type: SpanType, isSelected: boolean): string {
    const opacity = isSelected ? '' : 'opacity-70';
    switch (type) {
      case 'root':    return `bg-primary-300 border-primary-600 ${opacity}`;
      case 'llm':     return `bg-secondary-200 border-secondary-600 ${opacity}`;
      case 'tool':    return `bg-retro-orange-200 border-retro-orange-600 ${opacity}`;
      case 'error':   return `bg-error-200 border-error-600 ${opacity}`;
      case 'slow':    return `bg-warning-200 border-warning-600 ${opacity}`;
      default:        return `bg-gray-200 border-gray-500 ${opacity}`;
    }
  }

  function getSpanPosition(span: TraceSpan): { left: number; width: number } {
    const spanStart = new Date(span.start_time).getTime();
    const traceStart = new Date(spans[0].start_time).getTime();
    const offset = spanStart - traceStart;
    const duration = span.duration_ms || 0;
    return {
      left: totalDuration > 0 ? (offset / totalDuration) * 100 : 0,
      width: totalDuration > 0 ? Math.max((duration / totalDuration) * 100, 0.3) : 0.3,
    };
  }

  // ─── Tree helpers ────────────────────────────────────────────────────────

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

  function getAllDescendants(spanId: string, parentChildMap: Map<string, TraceSpan[]>): TraceSpan[] {
    const children = parentChildMap.get(spanId) || [];
    const descendants: TraceSpan[] = [...children];
    for (const child of children) {
      descendants.push(...getAllDescendants(child.span_id, parentChildMap));
    }
    return descendants;
  }

  function isLastSibling(span: TraceSpan, allSpans: TraceSpan[], parentChildMap: Map<string, TraceSpan[]>): boolean {
    if (!span.parent_span_id) return true;
    const siblings = parentChildMap.get(span.parent_span_id) || [];
    if (siblings.length === 0) return true;
    const siblingIndices = siblings.map(s => allSpans.findIndex(sp => sp.span_id === s.span_id));
    const currentIndex = allSpans.findIndex(s => s.span_id === span.span_id);
    return Math.max(...siblingIndices) === currentIndex;
  }

  function shouldDrawVerticalLine(span: TraceSpan, depth: number, allSpans: TraceSpan[], parentChildMap: Map<string, TraceSpan[]>): boolean {
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
      const descendantIndices = getAllDescendants(sibling.span_id, parentChildMap)
        .map(d => allSpans.findIndex(s => s.span_id === d.span_id));
      if (descendantIndices.some(idx => idx > currentIndex)) return true;
    }
    return false;
  }

  function sortSpansDepthFirst(spans: TraceSpan[]): TraceSpan[] {
    const childrenMap = new Map<string | null, TraceSpan[]>();
    for (const span of spans) {
      const parentId = span.parent_span_id || null;
      if (!childrenMap.has(parentId)) childrenMap.set(parentId, []);
      childrenMap.get(parentId)!.push(span);
    }
    for (const siblings of childrenMap.values()) {
      siblings.sort((a, b) => {
        const tA = new Date(a.start_time).getTime();
        const tB = new Date(b.start_time).getTime();
        return tA !== tB ? tA - tB : a.span_order - b.span_order;
      });
    }
    const result: TraceSpan[] = [];
    function traverse(parentId: string | null) {
      for (const child of childrenMap.get(parentId) || []) {
        result.push(child);
        traverse(child.span_id);
      }
    }
    traverse(null);
    return result;
  }

  const sortedSpans = $derived(sortSpansDepthFirst(spans));
  const parentChildMap = $derived(buildParentChildMap(sortedSpans));

  // ─── Scroll sync ─────────────────────────────────────────────────────────

  function onSpanScroll() {
    if (isTimelineScrolling) return;
    isSpanScrolling = true;
    if (timelineScrollContainer) timelineScrollContainer.scrollTop = spanScrollContainer.scrollTop;
    requestAnimationFrame(() => { isSpanScrolling = false; });
  }

  function onTimelineScroll() {
    if (isSpanScrolling) return;
    isTimelineScrolling = true;
    if (spanScrollContainer) spanScrollContainer.scrollTop = timelineScrollContainer.scrollTop;
    requestAnimationFrame(() => { isTimelineScrolling = false; });
  }

  // ─── Hover cursor tracking ────────────────────────────────────────────────

  function onTimelineMouseMove(e: MouseEvent) {
    if (!timelineScrollContainer) return;
    const rect = timelineScrollContainer.getBoundingClientRect();
    hoverX = ((e.clientX - rect.left) / rect.width) * 100;
  }

  function onTimelineMouseLeave() {
    hoverX = null;
  }
</script>

<div class="flex flex-col h-full bg-white text-sm overflow-hidden">

  <!-- Column Headers / Axis -->
  <div class="flex-shrink-0 bg-surface-50 border-b-2 border-black z-10">
    <div class="flex h-9">

      <!-- Left column header -->
      <div class="w-[32%] min-w-[220px] flex items-center px-3 border-r-2 border-black flex-shrink-0">
        <span class="text-xs font-black uppercase tracking-widest text-black">Span</span>
      </div>

      <!-- Timeline axis -->
      <div class="flex-1 relative flex items-end px-0 pb-1.5 overflow-hidden">
        {#each AXIS_MARKS as mark, i}
          {@const pct = mark * 100}
          <div
            class="absolute bottom-0 flex flex-col items-center pointer-events-none"
            style="left: {pct}%; transform: translateX({i === 0 ? '0' : i === AXIS_MARKS.length - 1 ? '-100%' : '-50%'});"
          >
            <div class="w-px bg-black/20" style="height: 6px;"></div>
            <span class="text-[10px] font-mono text-gray-500 leading-tight mt-0.5 whitespace-nowrap">
              {formatDuration(totalDuration * mark)}
            </span>
          </div>
          <!-- Full-height tick line -->
          {#if i > 0}
            <div
              class="absolute top-0 bottom-0 w-px bg-black/8 pointer-events-none"
              style="left: {pct}%;"
            ></div>
          {/if}
        {/each}
        <span class="absolute top-1.5 right-2 text-[10px] font-black uppercase tracking-widest text-black/40">Timeline</span>
      </div>
    </div>
  </div>

  <!-- Span rows (locked scroll) -->
  <div class="flex flex-1 min-h-0 overflow-hidden">

    <!-- Left: Span names -->
    <div
      bind:this={spanScrollContainer}
      onscroll={onSpanScroll}
      class="w-[32%] min-w-[220px] flex-shrink-0 overflow-auto border-r-2 border-black bg-surface-50"
    >
      {#each sortedSpans as span (span.span_id)}
        {@const isSelected = selectedSpan?.span_id === span.span_id}
        {@const indent = span.depth * INDENT_PX}
        {@const type = getSpanType(span)}
        {@const typeColor = getTypeColor(type)}
        {@const isLast = isLastSibling(span, sortedSpans, parentChildMap)}
        {@const hasChildren = (parentChildMap.get(span.span_id) || []).length > 0}

        <div
          class="flex items-center gap-1.5 pr-2 cursor-pointer transition-colors border-b border-gray-100 relative min-w-max
            {isSelected
              ? 'bg-primary-50 border-l-4 border-l-primary-600'
              : 'hover:bg-surface-100 border-l-4 border-l-transparent'}"
          style="height: {ROW_HEIGHT}px; padding-left: calc({indent}px + 0.5rem);"
          onclick={() => onSpanSelect(span)}
          onkeydown={(e) => e.key === 'Enter' && onSpanSelect(span)}
          role="button"
          tabindex="0"
        >
          <!-- Tree connector lines -->
          {#if span.depth > 0}
            {#each Array.from({ length: span.depth }) as _, depthIndex}
              {@const shouldDrawLine = shouldDrawVerticalLine(span, depthIndex, sortedSpans, parentChildMap)}
              {@const isCurrentLevel = depthIndex === span.depth - 1}
              {@const lineLeft = depthIndex * INDENT_PX + 8}

              <div
                class="absolute pointer-events-none"
                style="left: calc({lineLeft}px + 0.5rem); width: 1px; top: 0; height: {ROW_HEIGHT}px;"
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

          <!-- Span type color square -->
          <span class="z-10 flex-shrink-0 w-3 h-3 border {typeColor} rounded-sm"></span>

          <!-- Child chevron indicator -->
          {#if hasChildren}
            <ChevronRight class="w-3 h-3 text-gray-400 flex-shrink-0 -mx-0.5" />
          {/if}

          <!-- Span name -->
          <span class="text-xs font-mono truncate {isSelected ? 'text-primary-900 font-bold' : 'text-gray-800'}" style="max-width: 180px;">
            {span.span_name}
          </span>

          <!-- Slow indicator -->
          {#if slowestSpan && span.span_id === slowestSpan.span_id}
            <Clock class="w-3 h-3 text-warning-600 flex-shrink-0 ml-auto" />
          {/if}

          <!-- Error indicator -->
          {#if hasSpanError(span)}
            <CircleX class="w-3 h-3 text-error-600 flex-shrink-0 ml-auto" />
          {/if}
        </div>
      {/each}
    </div>

    <!-- Right: Timeline bars -->
    <div
      bind:this={timelineScrollContainer}
      onscroll={onTimelineScroll}
      onmousemove={onTimelineMouseMove}
      onmouseleave={onTimelineMouseLeave}
      role="presentation"
      class="flex-1 overflow-y-auto overflow-x-hidden relative"
    >
      <!-- Vertical tick grid lines behind rows -->
      {#each AXIS_MARKS.slice(1) as mark}
        <div
          class="absolute top-0 bottom-0 w-px bg-black/6 pointer-events-none z-0"
          style="left: {mark * 100}%;"
          role="presentation"
        ></div>
      {/each}

      <!-- Hover cursor line -->
      {#if hoverX !== null}
        <div
          class="absolute top-0 bottom-0 w-px bg-black/30 pointer-events-none z-20"
          style="left: {hoverX}%;"
        ></div>
      {/if}

      {#each sortedSpans as span (span.span_id)}
        {@const position = getSpanPosition(span)}
        {@const isSelected = selectedSpan?.span_id === span.span_id}
        {@const type = getSpanType(span)}
        {@const barColor = getBarColor(type, isSelected)}

        <div
          class="flex items-center px-2 cursor-pointer transition-colors border-b border-gray-100 relative z-10
            {isSelected ? 'bg-primary-50' : 'hover:bg-surface-100'}"
          style="height: {ROW_HEIGHT}px;"
          onclick={() => onSpanSelect(span)}
          onkeydown={(e) => e.key === 'Enter' && onSpanSelect(span)}
          role="button"
          tabindex="0"
        >
          <div class="relative flex-1 h-[18px] min-w-0">
            <!-- Span bar -->
            <div
              class="absolute h-full border rounded-sm transition-all duration-150 {barColor} {isSelected ? 'shadow-small' : ''}"
              style="left: {position.left}%; width: {position.width}%;"
            >
              <!-- Duration label inside bar if wide enough -->
              {#if position.width > 12}
                <span class="absolute inset-0 flex items-center justify-center text-[10px] font-mono px-1 truncate text-black/70">
                  {formatDuration(span.duration_ms)}
                </span>
              {/if}
            </div>
          </div>

          <!-- Duration label outside bar (always visible, right-aligned) -->
          <span class="w-14 text-[10px] font-mono text-gray-500 text-right flex-shrink-0 whitespace-nowrap">
            {formatDuration(span.duration_ms)}
          </span>
        </div>
      {/each}
    </div>

  </div>

</div>
