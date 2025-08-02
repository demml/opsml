<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import type { Message, Prompt } from '../card_interfaces/promptcard';
  import { onMount } from 'svelte';
  import "$lib/styles/hljs.css";


  let { prompt} = $props<{prompt: Prompt;}>();
  let openState = $state(false);
  let copiedButton = $state<'user' | 'system' | null>(null);
  let user_messages: string = $state('');
  let system_messages: string = $state('');
  let timeoutId: number = 0;


  function modalClose() {
      openState = false;
  }



  async function copyToClipboard(code: string, buttonType: 'user' | 'system'): Promise<void> {
    try {
      await navigator.clipboard.writeText(code);
      copiedButton = buttonType;
      
      // Reset the copied state after 2 seconds
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        copiedButton = null;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  }

  function formatMessages(messages: Message[]): string {
    return JSON.stringify(
      messages.map(message => ({
        content: Object.values(message.content)[0]
      })),
      null,
      2
    );
  }

  onMount(() => {
    user_messages = formatMessages(prompt.user_message);
    system_messages = formatMessages(prompt.system_message);
  });
  
  
  </script>
  
 
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
  contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-xl w-[700px] max-h-[700px] overflow-auto"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Prompt Messages{/snippet}
  {#snippet content()}
    <div class="flex flex-row pb-2 justify-between items-center pr-2">
      <header class="text-lg font-bold text-primary-800">Messages</header> 
    </div>

    <div class="flex flex-col gap-2">
      <div>
        <div class="flex flex-row pb-2 justify-between items-center pr-2">
          <header class="font-bold text-black">User Messages</header> 
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" 
            onclick={() => copyToClipboard(user_messages, 'user')} 
            disabled={!user_messages}
          >
            {copiedButton === 'user' ? 'Copied 👍' : 'Copy'}
          </button>
        </div>
        <div class="overflow-auto">
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[200px] text-sm">
            <Highlight language={json} code={user_messages} let:highlighted>
              <LineNumbers {highlighted} hideBorder wrapLines />
            </Highlight>
          </div>
        </div>
      </div>

      <div>
        <div class="flex flex-row pb-2 justify-between items-center pr-2">
          <header class="font-bold text-black">System Messages</header> 
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" 
            onclick={() => copyToClipboard(system_messages, 'system')} 
            disabled={!system_messages}
          >
            {copiedButton === 'system' ? 'Copied 👍' : 'Copy'}
          </button>
        </div>
        <div class="overflow-auto">
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[200px] text-sm">
            <Highlight language={json} code={system_messages} let:highlighted>
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

