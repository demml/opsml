<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import type { Message, Prompt } from '../card_interfaces/promptcard';
  import { onMount } from 'svelte';
  import "$lib/styles/hljs.css";
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';


  let { prompt} = $props<{prompt: Prompt;}>();
  let openState = $state(false);
  let copiedButton = $state<'user' | 'system' | null>(null);
  let messages: string = $state('');
  let system_instructions: string = $state('');
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
    messages = formatMessages(prompt.message);
    system_instructions = formatMessages(prompt.system_instruction);
  });
  
  
  </script>
  
 
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
  contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-lg max-h-[42rem] overflow-auto"
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
            onclick={() => copyToClipboard(messages, 'user')} 
            disabled={!messages}
          >
            {copiedButton === 'user' ? 'Copied 👍' : 'Copy'}
          </button>
        </div>
        <div class="overflow-auto">
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[20rem] text-sm">
            <CodeBlock lang="json" code={messages} showLineNumbers={false} />
          </div>
        </div>
      </div>

      <div>
        <div class="flex flex-row pb-2 justify-between items-center pr-2">
          <header class="font-bold text-black">System Messages</header> 
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" 
            onclick={() => copyToClipboard(system_instructions, 'system')} 
            disabled={!system_instructions}
          >
            {copiedButton === 'system' ? 'Copied 👍' : 'Copy'}
          </button>
        </div>
        <div class="overflow-auto">
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[20rem] text-sm">
            <CodeBlock lang="json" code={system_instructions} showLineNumbers={false} />
          </div>
        </div>
      </div>
    </div>

    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
    </footer>
  {/snippet}
  </Modal>

