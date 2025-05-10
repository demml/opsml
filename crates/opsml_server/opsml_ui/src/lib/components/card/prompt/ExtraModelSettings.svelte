<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import Highlight, { LineNumbers } from "svelte-highlight";
    import json from "svelte-highlight/languages/json";
    import type { ModelSettings } from '../card_interfaces/promptcard';
    import { onMount } from 'svelte';
  
  
    let { settings } = $props<{settings: ModelSettings;}>();
    let openState = $state(false);

    let logit_bias: string = $state('');
    let stop_sequences: string = $state('');
    let extra_body: string = $state('');
  
  
    function modalClose() {
        openState = false;
    }
  
    function formatbias(bias: Record<string, number>): string {
      return JSON.stringify(
        Object.entries(bias).map(([key, value]) => ({ [key]: value })),
        null,
        2
      );
    }

    function formatStopSequences(sequences: string[]): string {
      return JSON.stringify(sequences, null, 2);
    }
    function formatExtraBody(body: string): string {
      return JSON.stringify(body, null, 2);
    }
  
    onMount(() => {

        // if logit_bias is not empty, format it
        if (settings.logit_bias) {
            logit_bias = formatbias(settings.logit_bias);
        }

        // if stop is not empty, format it
        if (settings.stop_sequences) {
            stop_sequences = formatStopSequences(settings.stop_sequences);
        }

        // if extra_body is not empty, format it
        if (settings.extra_body) {
            extra_body = formatExtraBody(settings.extra_body);
        }

    });
    
    
    </script>
    
   
    <Modal
    open={openState}
    onOpenChange={(e) => (openState = e.open)}
    triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
    contentBase="card p-2 bg-slate-100 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[700px]"
    backdropClasses="backdrop-blur-sm"
    >
    {#snippet trigger()}Extra Settings{/snippet}
    {#snippet content()}
      <div class="flex flex-row pb-3 justify-between items-center pr-2">
        <header class="text-xl font-bold text-primary-800">Extra Model Settings</header> 
      </div>
  
      <div class="flex flex-col gap-2">
        <div>
          <div class="flex flex-row pb-3 justify-between items-center pr-2">
            <header class="text-lg font-bold text-black">Logit Bias</header> 
          </div>
          <div class="overflow-auto px-4">
            <div class="rounded-lg border-2 border-black overflow-hidden">
              <Highlight language={json} code={logit_bias} let:highlighted>
                <LineNumbers {highlighted} hideBorder wrapLines />
              </Highlight>
            </div>
          </div>
        </div>
  
        <div>
          <div class="flex flex-row pb-3 justify-between items-center pr-2">
            <header class="text-lg font-bold text-black">Stop Sequences</header> 
          </div>
          <div class="overflow-auto px-4">
            <div class="rounded-lg border-2 border-black overflow-hidden">
              <Highlight language={json} code={stop_sequences} let:highlighted>
                <LineNumbers {highlighted} hideBorder wrapLines />
              </Highlight>
            </div>
          </div>
        </div>

        <div>
          <div class="flex flex-row pb-3 justify-between items-center pr-2">
            <header class="text-lg font-bold text-black">Extra Arguments</header> 
          </div>
          <div class="overflow-auto px-4">
            <div class="rounded-lg border-2 border-black overflow-hidden">
              <Highlight language={json} code={extra_body} let:highlighted>
                <LineNumbers {highlighted} hideBorder wrapLines />
              </Highlight>
            </div>
          </div>
        </div>

      </div>
  
      <footer class="flex justify-end gap-4 p-2">
        <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
      </footer>
    {/snippet}
    </Modal>
    