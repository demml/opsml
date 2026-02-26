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

  let visible = $state(false);

  onMount(() => {
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(() => { visible = true; });
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });

  function handleClose() {
    visible = false;
    setTimeout(onClose, 200);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') handleClose();
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) handleClose();
  }
</script>

<!-- Backdrop -->
<div
  role="dialog"
  aria-modal="true"
  aria-label="Trace detail"
  class="fixed top-14 inset-0 z-50 flex justify-end transition-opacity duration-200 ease-out {visible ? 'opacity-100' : 'opacity-0'}"
  onkeydown={handleKeydown}
  onclick={handleBackdropClick}
  style="background: rgba(0,0,0,0.35);"
  tabindex=0
>
  <!-- Right-side drawer panel — 80% width -->
  <div
    class="flex flex-col h-full bg-surface-50 border-l-4 border-black shadow transition-transform duration-200 ease-out {visible ? 'translate-x-0' : 'translate-x-full'}"
    style="width: 80%;"
    role="presentation"
    onclick={(e) => e.stopPropagation()}
  >
    <TraceDetailContent {trace} {traceSpans} onClose={handleClose} showCloseButton={true} />
  </div>
</div>
