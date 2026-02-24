<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { type TraceListItem, type TraceSpansResponse } from './types';
  import TraceDetailContent from './TraceDetailContent.svelte';

  let {
    trace,
    traceSpans,
    onClose,
  }: {
    trace: TraceListItem;
    traceSpans: TraceSpansResponse;
    onClose: () => void;
  } = $props();

  let isClosing = $state(false);

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      onClose();
    }, 20);
  }

  onMount(() => {
    document.body.style.overflow = 'hidden';
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });
</script>

<!-- Backdrop -->
<div
  class="fixed inset-x-0 bottom-0 top-14 bg-black/30 z-40 transition-opacity duration-300"
  class:opacity-0={isClosing}
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close panel backdrop"
></div>

<!-- Side Panel -->
<div
  class="fixed top-14 right-0 h-[calc(100%-3.5rem)] w-full lg:w-4/5 xl:w-3/4 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <TraceDetailContent {trace} {traceSpans} onClose={handleClose} showCloseButton={true} />
</div>