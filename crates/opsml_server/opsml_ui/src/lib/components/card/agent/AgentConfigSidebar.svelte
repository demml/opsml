<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Settings, X, ChevronRight } from 'lucide-svelte';

  let {
    config,
    onClose,
  }: {
    config: {
      endpoint: string;
      method: string;
      headers: string;
      params: string;
      timeout: number;
    };
    onClose: () => void;
  } = $props();

  let isClosing = $state(false);

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      onClose();
    }, 20);
  }

  function handleTabKey(e: KeyboardEvent) {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.target as HTMLTextAreaElement;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const value = target.value;
      const tabChar = '  '; // 2 spaces for JSON
      
      if (e.shiftKey) {
        // Shift+Tab: Unindent (remove leading spaces from current line)
        const lineStart = value.lastIndexOf('\n', start - 1) + 1;
        const lineEnd = value.indexOf('\n', start);
        const actualLineEnd = lineEnd === -1 ? value.length : lineEnd;
        const line = value.substring(lineStart, actualLineEnd);
        
        // Remove up to 2 leading spaces
        const unindented = line.replace(/^  ?/, '');
        const removed = line.length - unindented.length;
        
        if (removed > 0) {
          target.value = value.substring(0, lineStart) + unindented + value.substring(actualLineEnd);
          target.selectionStart = target.selectionEnd = Math.max(lineStart, start - removed);
        }
      } else {
        // Tab: Indent (insert 2 spaces)
        target.value = value.substring(0, start) + tabChar + value.substring(end);
        target.selectionStart = target.selectionEnd = start + tabChar.length;
      }
      
      // Trigger input event to update Svelte binding
      target.dispatchEvent(new Event('input', { bubbles: true }));
    }
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
  aria-label="Close configuration sidebar"
></div>

<!-- Side Panel -->
<div
  class="fixed top-0 right-0 h-full w-full lg:w-2/5 xl:w-1/3 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <!-- Header -->
  <div class="flex items-center justify-between p-6 border-b-2 border-black bg-gradient-primary flex-shrink-0">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-white rounded-lg border-2 border-black shadow-small">
        <Settings class="w-5 h-5 text-primary-800" />
      </div>
      <div>
        <h3 class="text-lg font-bold text-white">Configuration</h3>
        <p class="text-xs text-white/80">Request settings</p>
      </div>
    </div>

    <button
      onclick={handleClose}
      class="p-2 bg-white text-primary-800 hover:bg-surface-100 rounded-lg transition-colors border-2 border-black shadow-small"
      aria-label="Close sidebar"
    >
      <X class="w-5 h-5" />
    </button>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-y-auto p-6 space-y-4">
    <!-- Endpoint -->
    <div>
      <label for="endpoint-input" class="text-sm font-bold text-primary-800 block mb-2">Endpoint URL</label>
      <input
        id="endpoint-input"
        type="text"
        bind:value={config.endpoint}
        class="w-full text-sm px-3 py-2 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-small"
        placeholder="https://api.example.com/agent"
      />
      <p class="text-xs text-gray-600 mt-1">The API endpoint for your agent</p>
    </div>

    <!-- Method and Timeout -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label for="method-select" class="text-sm font-bold text-primary-800 block mb-2">HTTP Method</label>
        <select
          id="method-select"
          bind:value={config.method}
          class="w-full text-black text-sm px-3 py-2 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-small bg-white"
        >
          <option value="POST">POST</option>
          <option value="GET">GET</option>
          <option value="PUT">PUT</option>
          <option value="PATCH">PATCH</option>
        </select>
      </div>

      <div>
        <label for="timeout-input" class="text-sm font-bold text-primary-800 block mb-2">Timeout (ms)</label>
        <input
          id="timeout-input"
          type="number"
          bind:value={config.timeout}
          class="w-full text-black text-sm px-3 py-2 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-small"
          min="1000"
          step="1000"
        />
      </div>
    </div>

    <!-- Headers -->
    <div>
      <label for="headers-textarea" class="text-sm font-bold text-primary-800 block mb-2">Headers</label>
      <div class="bg-surface-50 border-2 border-black rounded-lg shadow-small overflow-hidden">
        <textarea
          id="headers-textarea"
          bind:value={config.headers}
          onkeydown={handleTabKey}
          rows="5"
          class="w-full text-xs text-black px-3 py-2 focus:ring-primary-500 font-mono bg-transparent resize-none block"
          placeholder={'{"Content-Type": "application/json"}'}
        ></textarea>
      </div>
      <p class="text-xs text-gray-600 mt-1">JSON object with request headers</p>
    </div>

    <!-- Additional Parameters -->
    <div>
      <label for="params-textarea" class="text-sm font-bold text-primary-800 block mb-2">Additional Parameters</label>
      <div class="bg-surface-50 border-2 border-black rounded-lg shadow-small overflow-hidden">
        <textarea
          id="params-textarea"
          bind:value={config.params}
          onkeydown={handleTabKey}
          rows="5"
          class="w-full text-xs text-black px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono bg-transparent resize-none block"
          placeholder={'{"temperature": 0.7, "max_tokens": 1000}'}
        ></textarea>
      </div>
      <p class="text-xs text-gray-600 mt-1">JSON object with additional request parameters</p>
    </div>

    <!-- Info Box -->
    <div class="bg-primary-50 border-2 border-primary-800 rounded-lg p-4 shadow-small">
      <div class="flex items-start gap-2">
        <Settings class="w-4 h-4 text-primary-800 flex-shrink-0 mt-0.5" />
        <div>
          <p class="text-sm font-bold text-primary-900">Configuration Tips</p>
          <ul class="text-xs text-primary-800 mt-2 space-y-1 list-disc list-inside">
            <li>Headers and parameters must be valid JSON</li>
            <li>Timeout should be sufficient for your agent's response time</li>
            <li>Configuration persists during your session</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="p-4 border-t-2 border-black bg-surface-50 flex-shrink-0">
    <button
      onclick={handleClose}
      class="w-full py-2 bg-primary-500 text-white font-bold rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all flex items-center justify-center gap-2"
    >
      Apply Configuration
      <ChevronRight class="w-4 h-4" />
    </button>
  </div>
</div>
