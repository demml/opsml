<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import { onMount } from 'svelte';
    import Highlight, { LineNumbers } from "svelte-highlight";
    import python from "svelte-highlight/languages/python";
  import type { Feature, FeatureSchema } from './card_interfaces/datacard';
  
    let { schema } = $props<{schema: FeatureSchema}>();
    let openState = $state(false);
    let copied = $state(false);
    let timeoutId: number = 0;
  
  
    function modalClose() {
        openState = false;
    }
  
  
    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(JSON.stringify(schema, null, 2));
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
  contentBase="card p-2 bg-surface-50 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[700px]"
  backdropClasses="backdrop-blur-sm"
>
  {#snippet trigger()}Show Features{/snippet}
  {#snippet content()}
  <div class="mx-auto rounded-2xl bg-surface-50 p-4 md:px-5 flex flex-col">
    <!-- Header -->
    <div class="flex flex-row pb-2 justify-between items-center">
      <header class="text-lg font-bold text-primary-800">Feature Schema</header> 
      <button class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={copyToClipboard} disabled={copied}>
        {copied ? 'Copied 👍' : 'Copy'}
      </button>
    </div>
    
    <!-- Table Container -->
    <div class="overflow-auto max-h-[550px]">
      <div class="rounded-lg border-2 border-black overflow-hidden">
        <table class="w-full text-black text-sm bg-slate-100">
          <thead class="bg-primary-500">
            <tr>
              <th class="text-black text-sm pl-4 py-2 text-left whitespace-nowrap font-semibold">Name</th>
              <th class="text-black text-sm p-2 text-center whitespace-nowrap font-semibold">Feature Type</th>
              <th class="text-black text-sm pr-4 py-2 text-center whitespace-nowrap font-semibold">Shape</th>
            </tr>
          </thead>
          <tbody>
            {#each Object.entries(schema.items) as [name, feature]}
              <tr class="border-t hover:bg-primary-300">
                <td class="pl-4 text-sm py-2">{name}</td>
                <td class="p-2 text-sm text-center">{(feature as Feature).feature_type}</td>
                <td class="pr-4 py-2 text-sm text-center">{(feature as Feature).shape.toString()}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer -->
    <footer class="flex justify-end gap-4 p-2 mt-6">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
    </footer>
  </div>
  {/snippet}
</Modal>
  