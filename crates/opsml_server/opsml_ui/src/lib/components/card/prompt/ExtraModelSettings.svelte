<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import Highlight, { LineNumbers } from "svelte-highlight";
    import json from "svelte-highlight/languages/json";
    import { onMount } from 'svelte';


    let { settings } = $props<{settings: Record<string, any>; }>();
    let openState = $state(false);
    let formattedSettings = $state("");
    let copied = $state(false);
    let timeoutId: number = 0;

  
  
    function modalClose() {
        openState = false;
    }

    function formatsettings(settings: Record<string, any>): string {
      return JSON.stringify(settings, null, 2);
    }

    onMount(() => {
      formattedSettings = formatsettings(settings);
    });

    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(formattedSettings);
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
    triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
    contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[800px] overflow-auto"
    backdropClasses="backdrop-blur-sm"
    >
    {#snippet trigger()}Settings{/snippet}
    {#snippet content()}
      <div class="mx-auto rounded-2xl p-4 md:px-5 flex flex-col h-full">
        <div class="flex flex-row pb-2 justify-between items-center flex-shrink-0">
          <header class="text-lg font-bold text-primary-800">Provider Settings</header> 
          <button class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={copyToClipboard} disabled={copied}>
            {copied ? 'Copied 👍' : 'Copy'}
          </button>
        </div>

        <div class="flex flex-col gap-2">
          <div class="overflow-auto">
            <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[600px] text-sm">
              <Highlight language={json} code={formattedSettings} let:highlighted>
                <LineNumbers {highlighted} hideBorder wrapLines />
              </Highlight>
            </div>
          </div>
        </div>

         <footer class="flex justify-end gap-4 p-2">
          <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
        </footer>

      </div>
  
      
  
     
    {/snippet}
    </Modal>
    