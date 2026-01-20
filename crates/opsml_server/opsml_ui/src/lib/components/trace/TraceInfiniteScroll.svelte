<script lang="ts">
  import type { TraceListItem, TracePaginationResponse, TraceCursor, TracePageFilter } from './types';
  import VirtualScroller from '$lib/components/utils/VirtualScroller.svelte';
  import { getServerTracePage } from './utils';
  /**
   * True infinite scroll with virtual positioning.
   * Maintains a sliding window of items while allowing unlimited scrolling.
   */

  let {
    initialPage,
    filters,
    maxItems = 100,
    height = 'calc(100vh - 400px)',
    children
  }: {
    initialPage: TracePaginationResponse;
    filters: TracePageFilter;
    maxItems?: number;
    height?: string;
    children: (item: TraceListItem, index: number) => any;
  } = $props();

  // State management
  let allTraces = $state<TraceListItem[]>([...initialPage.items]);
  let hasNext = $state(initialPage.has_next);
  let hasPrevious = $state(initialPage.has_previous ?? false);
  let nextCursor = $state<TraceCursor | undefined>(initialPage.next_cursor);
  let previousCursor = $state<TraceCursor | undefined>(initialPage.previous_cursor);
  let isLoading = $state(false);

  let virtualOffset = $state(0);

  const ROW_HEIGHT = 40;
  const LOAD_THRESHOLD = 500;
  const PAGE_SIZE = 50;
  const TRIM_TRIGGER = maxItems + 30;
  const KEEP_ITEMS = maxItems;

  /**
   * Load previous page (newer traces)
   */
  async function loadPrevious() {
    if (!hasPrevious || !previousCursor || isLoading) return;
    isLoading = true;

    try {

      let response = await getServerTracePage(fetch, {
          ...filters.filters,
          limit: PAGE_SIZE,
          cursor_start_time: previousCursor.start_time,
          cursor_trace_id: previousCursor.trace_id,
          direction: 'previous'
      });


      const newTraces = response.items.filter(
        (newTrace) => !allTraces.some((t) => t.trace_id === newTrace.trace_id)
      );

      if (newTraces.length > 0) {
        allTraces = [...newTraces, ...allTraces];
        virtualOffset = Math.max(0, virtualOffset - newTraces.length);
      }

      hasPrevious = response.has_previous ?? false;
      previousCursor = response.previous_cursor;

      // Trim from bottom if we exceed the limit
      if (allTraces.length > TRIM_TRIGGER) {
        const newLength = KEEP_ITEMS;
        const trimmedTraces = allTraces.slice(0, newLength);
        allTraces = trimmedTraces;

        // Update cursors after trimming
        const lastItem = allTraces[allTraces.length - 1];
        nextCursor = {
          start_time: lastItem.start_time,
          trace_id: lastItem.trace_id
        };
        hasNext = true;
      }
    } catch (error) {
      console.error('❌ Failed to load previous traces:', error);
    } finally {
      isLoading = false;
    }
  }

  /**
   * Load next page (older traces)
   */
  async function loadNext() {
    if (!hasNext || !nextCursor || isLoading) return;

    isLoading = true;

    try {
      let response = await getServerTracePage(fetch, {
          ...filters.filters,
          limit: PAGE_SIZE,
          cursor_start_time: nextCursor.start_time,
          cursor_trace_id: nextCursor.trace_id,
          direction: 'next'
      });

      const newTraces = response.items.filter(
        (newTrace) => !allTraces.some((t) => t.trace_id === newTrace.trace_id)
      );

      if (newTraces.length > 0) {
        allTraces = [...allTraces, ...newTraces];
      }

      hasNext = response.has_next;
      nextCursor = response.next_cursor;

      // Trim from top if we exceed the limit
      if (allTraces.length > TRIM_TRIGGER) {
        const trimCount = allTraces.length - KEEP_ITEMS;
        const trimmedTraces = allTraces.slice(trimCount);

        // Update virtual offset to maintain scroll position
        virtualOffset += trimCount;
        allTraces = trimmedTraces;

        // Update cursors after trimming
        const firstItem = allTraces[0];
        previousCursor = {
          start_time: firstItem.start_time,
          trace_id: firstItem.trace_id
        };
        hasPrevious = true;
      }
    } catch (error) {
      console.error('❌ Failed to load next traces:', error);
    } finally {
      isLoading = false;
    }
  }
</script>

<VirtualScroller
  items={allTraces}
  itemHeight={ROW_HEIGHT}
  getItemKey={(trace) => trace.trace_id}
  overscan={15}
  loadThreshold={LOAD_THRESHOLD}
  {hasPrevious}
  {hasNext}
  {isLoading}
  {virtualOffset}
  onLoadPrevious={loadPrevious}
  onLoadNext={loadNext}
  {height}
>
  {#snippet children(item: TraceListItem, index: number)}
    {@render children(item, virtualOffset + index)}
  {/snippet}
</VirtualScroller>

{#if import.meta.env.DEV}
  <div class="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs font-mono space-y-1 max-w-xs shadow-lg z-50">
    <div class="font-bold border-b border-gray-600 pb-1 mb-1">🔍 Infinite Scroll Debug</div>
    <div class="text-green-400">Memory: {allTraces.length}/{maxItems} items</div>
    <div class="text-blue-400">Virtual: #{virtualOffset + 1} - #{virtualOffset + allTraces.length}</div>
    <div class="border-t border-gray-600 mt-1 pt-1"></div>
    <div>⬆️ Previous: {hasPrevious ? '✅' : '❌'}</div>
    <div>⬇️ Next: {hasNext ? '✅' : '❌'}</div>
    <div>⏳ Loading: {isLoading ? 'YES' : 'NO'}</div>
    {#if allTraces.length > 0}
      <div class="border-t border-gray-600 mt-1 pt-1 text-xs text-gray-400">
        <div>First: {new Date(allTraces[0].created_at).toLocaleTimeString()}</div>
        <div>Last: {new Date(allTraces[allTraces.length - 1].created_at).toLocaleTimeString()}</div>
      </div>
    {/if}
  </div>
{/if}