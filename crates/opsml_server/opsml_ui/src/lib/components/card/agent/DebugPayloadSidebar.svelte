<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import DebugPayloadContent from './DebugPayloadContent.svelte';
  import { X, Bug } from 'lucide-svelte';
  import type { DebugMessage } from './types';


  
  let {
    debugMessages,
    selectedIndex,
    onSelectIndex,
    onClose,
  }: {
    debugMessages: DebugMessage[];
    selectedIndex: number;
    onSelectIndex: (index: number) => void;
    onClose: () => void;
  } = $props();

  let isClosing = $state(false);

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      onClose();
    }, 20);
  }

  const selectedEntry = $derived.by(() => {
    const idx = debugMessages.findIndex(m => m.index === selectedIndex);
    const i = idx === -1 ? debugMessages.length - 1 : idx;
    return { message: debugMessages[i] };
  });

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
  class="fixed top-0 right-0 h-full w-full lg:w-4/5 xl:w-3/4 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b-2 border-black bg-gradient-primary flex-shrink-0">
    <div class="flex items-center gap-2">
      <Bug class="w-5 h-5 text-primary-950" />
      <h2 class="text-lg font-bold text-primary-950">Request & Response Debug</h2>
      <span class="badge bg-primary-100 text-primary-900 border-black border-1 shadow-small">
        {debugMessages.length} {debugMessages.length === 1 ? 'message' : 'messages'}
      </span>
    </div>
    <button
      onclick={handleClose}
      class="p-2 bg-white text-primary-800 hover:bg-surface-100 rounded-lg transition-colors border-2 border-black shadow-small"
      aria-label="Close debug panel"
    >
      <X class="w-5 h-5" />
    </button>
  </div>

  <!-- Split Layout -->
  <div class="flex flex-1 min-h-0">

    <!-- Left: Exchange History -->
    <div class="w-60 flex-shrink-0 border-r-2 border-black flex flex-col bg-surface-50">
      <div class="px-4 py-3 border-b-2 border-black bg-surface-200 flex-shrink-0">
        <p class="text-xs font-bold text-primary-900">Exchange History</p>
      </div>

      <div class="flex-1 overflow-auto">
        {#each debugMessages as debugMsg, i}
          {@const isSelected = debugMsg.index === selectedIndex}
          {@const isUser = debugMsg.role === 'user'}
          <button
            class="w-full text-left px-3 py-3 border-b border-gray-200 transition-colors cursor-pointer border-l-4 {isSelected ? (isUser ? 'bg-primary-100 border-l-primary-500' : 'bg-secondary-100 border-l-secondary-500') : 'border-l-transparent hover:bg-surface-200'}"
            onclick={() => onSelectIndex(debugMsg.index)}
          >
            <div class="flex items-center gap-2 mb-1">
              <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded {isUser ? 'bg-primary-100 text-primary-900 border border-primary-800' : 'bg-secondary-100 text-secondary-900 border border-secondary-800'}">
                {isUser ? 'User' : 'Agent'}
              </span>
              {#if debugMsg.messageId}
                <span class="text-[10px] font-mono text-gray-500">{debugMsg.messageId.slice(0, 8)}</span>
              {/if}
            </div>
            <p class="text-xs text-gray-700 truncate">
              {debugMsg.content.length > 36 ? debugMsg.content.slice(0, 36) + '…' : debugMsg.content}
            </p>
            <p class="text-[10px] font-mono text-gray-400 mt-1">
              {debugMsg.debugPayload.timestamp.toLocaleTimeString()}
            </p>
            {#if debugMsg.skillName}
              <p class="text-[10px] italic text-primary-700 truncate mt-0.5">{debugMsg.skillName}</p>
            {/if}
          </button>
        {/each}
      </div>
    </div>

    <!-- Right: Detail View -->
    <div class="flex-1 min-w-0 overflow-hidden">
      {#if selectedEntry.message}
        <DebugPayloadContent
          payload={selectedEntry.message.debugPayload}
          role={selectedEntry.message.role}
          skillName={selectedEntry.message.skillName}
        />
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500 p-4 text-center">
          Select an exchange to view details
        </div>
      {/if}
    </div>

  </div>
</div>
