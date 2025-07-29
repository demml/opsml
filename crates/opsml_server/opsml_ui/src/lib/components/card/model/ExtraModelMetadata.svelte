<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import Highlight, { LineNumbers } from "svelte-highlight";
    import json from "svelte-highlight/languages/json";
    import "$lib/styles/hljs.css";
  
    let { extra_metadata } = $props<{extra_metadata: any;}>();
    let openState = $state(false);

    function modalClose() {
        openState = false;
    }
  
    function formatExtraBody(body: any): string {
      return JSON.stringify(body, null, 2);
    }
  
    
    </script>
    
   
    <Modal
    open={openState}
    onOpenChange={(e) => (openState = e.open)}
    triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
    contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[800px] overflow-y-auto"
    backdropClasses="backdrop-blur-sm"
    >
    {#snippet trigger()}Model Metadata{/snippet}
    {#snippet content()}
      <div class="flex flex-row pb-3 justify-between items-center">
        <header class="text-lg font-bold text-primary-800">Model Specific Metadata</header> 
      </div>
  
      <div class="flex flex-col gap-2">
        <div>
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[600px] text-xs">
            <Highlight language={json} code={formatExtraBody(extra_metadata)} let:highlighted>
              <LineNumbers {highlighted} hideBorder wrapLines />
            </Highlight>
          </div>
        </div>

      </div>
  
      <footer class="flex justify-end gap-4 p-2">
        <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
      </footer>
    {/snippet}
    </Modal>
    