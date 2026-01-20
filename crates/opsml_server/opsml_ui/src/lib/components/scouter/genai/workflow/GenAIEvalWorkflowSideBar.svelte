<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { GenAIEvalWorkflowResult } from '../task';
  import GenAIEvalWorkflowContent from './GenAIEvalWorkflowContent.svelte';

  let {
    selectedWorkflow,
    onClose,
  }: {
    selectedWorkflow: GenAIEvalWorkflowResult;
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

<div
  class="fixed inset-0 bg-opacity-30 z-40 transition-opacity duration-300"
  class:opacity-0={isClosing}
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close panel backdrop"
></div>

<div
  class="fixed top-0 right-0 h-full w-full lg:w-4/5 xl:w-3/4 bg-white border-l-4 border-black shadow-2xl z-50 flex flex-col transition-transform duration-300"
  class:translate-x-full={isClosing}
>
  <GenAIEvalWorkflowContent workflow={selectedWorkflow} onClose={handleClose} showCloseButton={true} />
</div>