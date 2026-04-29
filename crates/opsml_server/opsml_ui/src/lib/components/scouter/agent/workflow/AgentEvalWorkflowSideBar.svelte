<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { AgentEvalWorkflowResult } from '../task';
  import AgentEvalWorkflowContent from './AgentEvalWorkflowContent.svelte';
  import type { AgentEvalProfile } from '../types';

  let {
    selectedWorkflow,
    onClose,
    profile,
    traceId,
  }: {
    selectedWorkflow: AgentEvalWorkflowResult;
    onClose: () => void;
    profile: AgentEvalProfile;
    traceId?: string;
  } = $props();

  let isClosing = $state(false);

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      onClose();
    }, 150);
  }

  onMount(() => {
    document.body.style.overflow = 'hidden';
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });
</script>

<!-- Backdrop: starts below navbar only, overlays subnav like trace sidebar -->
<div
  class="fixed inset-x-0 bottom-0 top-14 bg-black/20 z-30 transition-opacity duration-150 ease-out"
  class:opacity-0={isClosing}
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close panel backdrop"
></div>

<!-- Sidebar panel: positioned below navbar, overlays subnav -->
<div
  class="fixed right-0 bottom-0 top-14 w-full lg:w-4/5 xl:w-3/4
         bg-surface-50 border-l-2 border-black z-40 flex flex-col
         transition-transform duration-150 ease-out
         shadow-[-4px_0px_0px_0px_rgba(0,0,0,1)]"
  class:translate-x-full={isClosing}
>
  <AgentEvalWorkflowContent
    workflow={selectedWorkflow}
    onClose={handleClose}
    showCloseButton={true}
    profile={profile}
    {traceId}
  />
</div>
