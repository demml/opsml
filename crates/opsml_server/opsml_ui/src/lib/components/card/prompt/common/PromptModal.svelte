<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import type { Prompt } from '$lib/components/genai/types';
  import PromptViewer from './PromptViewer.svelte'; // The new component
  import { MessageSquareText, X } from 'lucide-svelte';

  let { prompt } = $props<{ prompt: Prompt }>();
  let openState = $state(false);

  function modalClose() {
    openState = false;
  }
</script>

<Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm flex items-center gap-2"
  contentBase="card p-0 bg-surface-50 border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden"
  backdropClasses="backdrop-blur-sm bg-black/20"
>
  {#snippet trigger()}
    <MessageSquareText class="w-4 h-4" />
    <span>View Messages</span>
  {/snippet}

  {#snippet content()}
    <header class="px-4 py-3 border-b-2 border-black bg-primary-500 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <MessageSquareText class="w-5 h-5" />
        <h2 class="text-xl font-black uppercase tracking-tight">Prompt Messages</h2>
      </div>
      <button
        onclick={modalClose}
        class="btn-icon btn-icon-sm bg-white border-2 border-black shadow-small shadow-hover-small"
      >
        <X class="w-4 h-4" color="black" />
      </button>
    </header>

    <div class="p-4 overflow-y-scroll flex-1 flex flex-col h-full bg-slate-50">
      <PromptViewer {prompt} />
    </div>

    <footer class="p-3 border-t-2 border-black bg-white flex justify-end shrink-0">
      <button
        type="button"
        class="btn text-sm bg-gray-200 text-black font-bold shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] border-black border-2 hover:translate-y-0.5 hover:shadow-none transition-all"
        onclick={modalClose}
      >
        Close
      </button>
    </footer>
  {/snippet}
</Modal>