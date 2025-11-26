<script lang="ts" generics="T">
  import { onMount, tick } from 'svelte';

  /**
   * Generic virtual scroller with bidirectional infinite scroll and virtual offset support.
   * Uses anchor-based scroll restoration to prevent jumping and loops.
   */

  type Props = {
    items: T[];
    itemHeight: number;
    overscan?: number;
    height?: string;
    onLoadPrevious?: () => Promise<void>;
    onLoadNext?: () => Promise<void>;
    loadThreshold?: number;
    hasPrevious?: boolean;
    hasNext?: boolean;
    isLoading?: boolean;
    virtualOffset?: number;
    /**
     * Function to extract a unique key from each item.
     * Falls back to index-based keys if not provided.
     */
    getItemKey?: (item: T, index: number) => string | number;
    children: (item: T, index: number) => any;
  };

  let {
    items = [],
    itemHeight,
    overscan = 15,
    height = '100%',
    onLoadPrevious,
    onLoadNext,
    loadThreshold = 500,
    hasPrevious = false,
    hasNext = false,
    isLoading = false,
    virtualOffset = 0,
    getItemKey = (_, index) => index,
    children
  }: Props = $props();

  let scrollContainer = $state<HTMLDivElement | null>(null);
  let scrollTop = $state(0);
  let containerHeight = $state(0);
  let isLoadingPrevious = $state(false);
  let isLoadingNext = $state(false);

  /**
   * Calculate visible range by mapping global scroll position to local array indices
   */
  const visibleRange = $derived.by(() => {
    if (!containerHeight || !itemHeight || items.length === 0) {
      return { start: 0, end: 0 };
    }

    const globalTopIndex = Math.floor(scrollTop / itemHeight);
    const globalBottomIndex = Math.ceil((scrollTop + containerHeight) / itemHeight);

    const localTopIndex = globalTopIndex - virtualOffset;
    const localBottomIndex = globalBottomIndex - virtualOffset;

    const start = Math.max(0, localTopIndex - overscan);
    const end = Math.max(start, Math.min(items.length, localBottomIndex + overscan));

    return { start, end };
  });

  /**
   * Items currently in the render window with computed keys
   */
  const visibleItems = $derived.by(() => {
    const { start, end } = visibleRange;
    return items.slice(start, end).map((item, i) => {
      const localIndex = start + i;
      const key = String(getItemKey(item, localIndex));

      return {
        item,
        index: localIndex,
        key
      };
    });
  });

  const totalHeight = $derived((virtualOffset + items.length) * itemHeight);
  const offsetY = $derived((virtualOffset + visibleRange.start) * itemHeight);

  /**
   * Handle scroll events with load triggers
   */
  function handleScroll(event: Event) {
    const target = event.target as HTMLDivElement;
    scrollTop = target.scrollTop;
    const scrollHeight = target.scrollHeight;
    const clientHeight = target.clientHeight;

    const startOfLoadedData = virtualOffset * itemHeight;
    const distanceFromStartOfLoadedData = scrollTop - startOfLoadedData;
    const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);

    // Trigger load previous
    if (
      hasPrevious &&
      !isLoadingPrevious &&
      !isLoading &&
      distanceFromStartOfLoadedData < loadThreshold &&
      onLoadPrevious
    ) {
      isLoadingPrevious = true;

      const firstVisible = visibleItems[0];
      if (!firstVisible) {
        onLoadPrevious().then(() => { isLoadingPrevious = false; });
        return;
      }

      const anchorKey = firstVisible.key;
      const anchorIndex = firstVisible.index;
      const offsetFromItemTop = scrollTop - ((virtualOffset + anchorIndex) * itemHeight);

      onLoadPrevious().then(async () => {
        await tick();

        if (scrollContainer) {
          // Find where anchor item moved to
          const newLocalIndex = items.findIndex((item, idx) => 
            String(getItemKey(item, idx)) === anchorKey
          );

          if (newLocalIndex !== -1) {
            // Calculate new absolute position
            const newGlobalIndex = virtualOffset + newLocalIndex;
            const newScrollTop = (newGlobalIndex * itemHeight) + offsetFromItemTop;

            // Only adjust if significantly different
            if (Math.abs(scrollContainer.scrollTop - newScrollTop) > 1) {
              scrollContainer.scrollTop = newScrollTop;
            }
          }
        }
        isLoadingPrevious = false;
      });
    }

    // Trigger load next
    if (
      hasNext &&
      !isLoadingNext &&
      !isLoading &&
      distanceFromBottom < loadThreshold &&
      onLoadNext
    ) {
      isLoadingNext = true;
      onLoadNext().then(() => {
        isLoadingNext = false;
      });
    }
  }

  onMount(() => {
    if (scrollContainer) {
      containerHeight = scrollContainer.clientHeight;
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          containerHeight = entry.contentRect.height;
        }
      });
      resizeObserver.observe(scrollContainer);
      return () => resizeObserver.disconnect();
    }
  });
</script>

<div
  bind:this={scrollContainer}
  class="virtual-scroller overflow-auto"
  style:height
  onscroll={handleScroll}
>
  <div class="virtual-scroller-spacer" style:height="{totalHeight}px" style:position="relative">
    {#if isLoadingPrevious}
      <div class="sticky top-0 left-0 right-0 flex justify-center py-2 bg-primary-50 border-b border-primary-200 z-20">
        <div class="flex items-center gap-2 text-sm text-primary-700">
          <div class="animate-spin h-4 w-4 border-2 border-primary-700 border-t-transparent rounded-full"></div>
          <span>Loading previous...</span>
        </div>
      </div>
    {/if}

    <div
      class="virtual-scroller-items"
      style:transform="translateY({offsetY}px)"
      style:position="absolute"
      style:top="0"
      style:left="0"
      style:right="0"
    >
      {#each visibleItems as { item, index, key } (key)}
        <div class="virtual-item" style:height="{itemHeight}px">
          {@render children(item, index)}
        </div>
      {/each}
    </div>

    {#if isLoadingNext}
      <div class="absolute bottom-0 left-0 right-0 flex justify-center py-2 bg-primary-50 border-t border-primary-200 z-20">
        <div class="flex items-center gap-2 text-sm text-primary-700">
          <div class="animate-spin h-4 w-4 border-2 border-primary-700 border-t-transparent rounded-full"></div>
          <span>Loading next...</span>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .virtual-scroller {
    position: relative;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .virtual-scroller-spacer {
    position: relative;
    width: 100%;
  }

  .virtual-scroller-items {
    will-change: transform;
  }

  .virtual-item {
    overflow: hidden;
  }
</style>