<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import type { GenAIEvalProfile } from '$lib/components/scouter/genai/types';
  import GenAITaskAccordion from '$lib/components/scouter/genai/task/GenAITaskAccordion.svelte';
  import { ListChecks, X, AlertCircle } from 'lucide-svelte';

  let { evalProfile } = $props<{ evalProfile: GenAIEvalProfile }>();
  let openState = $state(false);

  function modalClose() {
    openState = false;
  }

  const totalTaskCount = $derived(
    evalProfile.tasks.assertion.length +
    evalProfile.tasks.judge.length +
    evalProfile.tasks.trace.length
  );

  const hasNoTasks = $derived(totalTaskCount === 0);

</script>

<Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-secondary-500 text-black shadow shadow-hover border-black border-2 text-sm flex items-center gap-2"
  contentBase="card p-0 bg-surface-50 border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-6xl max-h-[85vh] flex flex-col overflow-hidden"
  backdropClasses="backdrop-blur-sm bg-black/20"
>
  {#snippet trigger()}
    <ListChecks class="w-4 h-4" />
    <span>Evaluation Tasks ({totalTaskCount})</span>
  {/snippet}

  {#snippet content()}
    <header class="px-4 py-3 border-b-2 border-black bg-secondary-500 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <ListChecks class="w-5 h-5" />
        <h2 class="text-xl font-black uppercase tracking-tight">Evaluation Tasks</h2>
      </div>
      <button
        onclick={modalClose}
        class="btn-icon btn-icon-sm bg-white border-2 border-black shadow-small shadow-hover-small"
      >
        <X class="w-4 h-4" color="black" />
      </button>
    </header>

    <div class="p-6 overflow-y-auto flex-1 flex flex-col bg-slate-50">
      {#if hasNoTasks}
        <div class="flex flex-col items-center justify-center h-full gap-4 text-center">
          <AlertCircle class="w-16 h-16 text-gray-400" />
          <div>
            <h3 class="text-lg font-bold text-gray-700">No Evaluation Tasks</h3>
            <p class="text-sm text-gray-500 mt-2">This prompt has no evaluation tasks defined.</p>
          </div>
        </div>
      {:else}
        <div class="space-y-4">
          <div class="flex items-center justify-between pb-3 border-b-2 border-black">
            <div>
              <h3 class="text-base font-bold text-primary-950">Task Breakdown</h3>
              <p class="text-xs text-gray-600 mt-1">
                {evalProfile.tasks.assertion.length} Assertion · 
                {evalProfile.tasks.judge.length} LLM Judge · 
                {evalProfile.tasks.trace.length} Trace
              </p>
            </div>
            {#if evalProfile.alias}
              <span class="badge text-xs border-1 px-3 py-1 bg-tertiary-100 text-tertiary-900 border-tertiary-800">
                Alias: {evalProfile.alias}
              </span>
            {/if}
          </div>

          <GenAITaskAccordion tasks={evalProfile.tasks} />
        </div>
      {/if}
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
