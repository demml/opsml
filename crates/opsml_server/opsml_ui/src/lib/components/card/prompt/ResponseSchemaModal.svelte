<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import type { Prompt } from '../card_interfaces/promptcard';
  import { onMount } from 'svelte';


  let { prompt} = $props<{prompt: Prompt;}>();
  let openState = $state(false);
  let copied = $state(false);
  let response_json_schema: string = $state('');
  let timeoutId: number = 0;


  function modalClose() {
      openState = false;
  }

  async function copyToClipboard(code: string): Promise<void> {
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


  onMount(() => {
    response_json_schema = JSON.stringify(prompt.response_json_schema, null, 2);
  });
  
  
  </script>
  
 
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
  contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[700px] overflow-auto"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Response Schema{/snippet}
  {#snippet content()}
    <div class="flex flex-row pb-2 justify-between items-center pr-2">
      <header class="text-lg font-bold text-primary-800">Schema</header> 
    </div>

    <div class="flex flex-col gap-2">
      <div>
        <div class="flex flex-row pb-2 justify-between items-center pr-2">
          <header class="font-bold text-black">Output</header> 
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" 
            onclick={() => copyToClipboard(response_json_schema)} 
            disabled={copied}
          >
            {copied ? 'Copied 👍' : 'Copy'}
          </button>
        </div>
        <div class="overflow-auto">
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[200px] text-sm">
            <Highlight language={json} code={response_json_schema} let:highlighted>
              <LineNumbers {highlighted} hideBorder wrapLines />
            </Highlight>
          </div>
        </div>
      </div>


    </div>

    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
    </footer>
  {/snippet}
  </Modal>
  