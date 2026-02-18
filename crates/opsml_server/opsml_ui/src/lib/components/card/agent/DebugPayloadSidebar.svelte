<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import DebugPayloadContent from './DebugPayloadContent.svelte';
  import { X } from 'lucide-svelte';

  interface DebugPayload {
    request: unknown;
    response: unknown;
    timestamp: Date;
  }

  let {
    payload,
    skillName,
    messageIndex,
    onClose,
  }: {
    payload: DebugPayload;
    skillName?: string;
    messageIndex: number;
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
  class="fixed inset-0 bg-opacity-30 z-40 transition-opacity duration-300"
  class:opacity-0={isClosing}
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close debug panel backdrop"
></div>

<!-- Side Panel -->
<div
  class="fixed top-0 right-0 h-full w-full lg:w-3/5 xl:w-1/2 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <!-- Header with Close Button -->
  <div class="flex items-center justify-between p-4 border-b-2 border-black bg-gradient-primary flex-shrink-0">
    <h2 class="text-lg font-bold text-white">Request & Response Debug</h2>
    <button
      onclick={handleClose}
      class="p-2 bg-white text-primary-800 hover:bg-surface-100 rounded-lg transition-colors border-2 border-black shadow-small"
      aria-label="Close debug panel"
    >
      <X class="w-5 h-5" />
    </button>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-hidden">
    <DebugPayloadContent {payload} {skillName} {messageIndex} />
  </div>
</div>
