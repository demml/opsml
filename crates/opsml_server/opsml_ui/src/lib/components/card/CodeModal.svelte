<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { onMount } from 'svelte';
  import { convertMarkdown } from '../readme/util';

  let { content } = $props<{content: string;}>();
  let openState = $state(false);
  let html = $state('');

  function modalClose() {
      openState = false;
  }

  
  onMount(async () => {
      html = await convertMarkdown(content);
      console.log('mounted');
  });

</script>

<Modal
open={openState}
onOpenChange={(e) => (openState = e.open)}
triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
contentBase="card bg-white p-4 border-2 border-black space-y-4 shadow  max-w-screen-sm"
backdropClasses="backdrop-blur-sm"
>
{#snippet trigger()}Use this card{/snippet}
{#snippet content()}
  <header class="flex justify-between">
    <h2 class="h3">Load Card</h2>
  </header>
  <article>
    <p class="w-100 h-24">
      {@html html}
    </p>
  </article>
  <footer class="flex justify-end gap-4">
    <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
    <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Confirm</button>
  </footer>
{/snippet}
</Modal>