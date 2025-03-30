<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import Highlight from "svelte-highlight";
    import json from "svelte-highlight/languages/json";
  
    let { code } = $props<{code: string; }>();
    let openState = $state(false);
    let copied = $state(false);
    let timeoutId: number = 0;
  
  
    function modalClose() {
        openState = false;
    }
  
    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(code);
        copied = true;
        
        // Reset the copied state after 2 seconds
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          copied = false;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text:', err);
      }
    }
  
  
  </script>
  
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
  contentBase="card p-2 bg-primary-500 border-2 border-black shadow max-w-screen-md"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Alert Details{/snippet}
  {#snippet content()}
    <div class="flex flex-row justify-between">
      <header class="pl-2 text-xl font-bold text-black">Alert Details</header> 
      <button class="btn bg-white text-black shadow shadow-hover border-black border-2 mr-3 mt-1" onclick={copyToClipboard} disabled={copied}>
        {copied ? 'Copied 👍' : 'Copy'}
      </button>
    </div>
    <div class="border-2 border-black m-2">
      <Highlight language={json}  
          code={code} 
          let:highlighted>
      </Highlight>
    </div>
    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn bg-white text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>    </footer>
  {/snippet}
  </Modal>
  
  
  