<script lang="ts">
  import { PromptHelper, type Prompt } from '$lib/components/genai/types';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import MessageBubble from './MessageBubble.svelte';
  import { Eye, Code, Copy, Check } from 'lucide-svelte';

  let { prompt } = $props<{ prompt: Prompt }>();

  // State
  let activeTab = $state<'preview' | 'json'>('preview');
  let copied = $state(false);

  // Derived Data
  let systemMessages = $derived(PromptHelper.getSystemInstructions(prompt));
  let chatMessages = $derived(PromptHelper.getMessages(prompt));
  let rawJson = $derived(JSON.stringify(prompt, null, 2));



  // Determine provider strictly
  let provider = $derived(prompt.provider);

  const tabs = [
    { id: 'preview', label: 'Preview', icon: Eye },
    { id: 'json', label: 'Raw JSON', icon: Code }
  ] as const;

  function copyJson() {
    navigator.clipboard.writeText(rawJson);
    copied = true;
    setTimeout(() => copied = false, 2000);
  }
</script>

<div class="flex flex-col h-full w-full">
  
  <div class="flex flex-row justify-between items-center pb-4 mb-2 border-b-2 border-black shrink-0">
    <div class="flex flex-col gap-2">
      <span class="text-xs font-black uppercase text-slate-500 tracking-wider">View Mode</span>
      <div class="flex p-1 bg-slate-100 border-2 border-black rounded-lg gap-1">
        {#each tabs as tab}
          <button
            class="flex items-center justify-center px-4 py-2 text-sm font-bold rounded-md border-2 transition-all duration-200
              {activeTab === tab.id
                ? 'bg-primary-500 text-black border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] -translate-x-[1px] -translate-y-[1px]'
                : 'bg-white text-slate-700 border-transparent hover:border-slate-300 hover:bg-slate-50'}"
            onclick={() => activeTab = tab.id}
          >
            <tab.icon class="w-4 h-4 mr-2" />
            {tab.label.toUpperCase()}
          </button>
        {/each}
      </div>
    </div>

    <div class="flex items-center gap-2 self-end">
      <div class="bg-black text-white text-xs font-bold px-3 py-1.5 rounded-md shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] border border-white/20">
        {prompt.provider} : {prompt.model}
      </div>
    </div>
  </div>

  <div class="flex-1 min-h-0 pr-2 relative">
    
    {#if activeTab === 'preview'}
      <div class="h-full overflow-y-auto flex flex-col gap-6 p-4">
        
        {#if systemMessages.length > 0}
          <div class="relative">
            <div class="absolute -top-3 left-0 bg-white border-2 border-black px-2 py-0.5 text-xs font-bold uppercase tracking-widest shadow z-10 text-black">
              System Instructions
            </div>
            <div class="flex flex-col gap-3 pt-4 border-l-2 border-dashed border-black/30 pl-4 ml-2 pt-6">
              {#each systemMessages as msg, i}
                <MessageBubble message={msg} {provider} index={i} />
              {/each}
            </div>
          </div>
        {/if}

        {#if chatMessages.length > 0}
           <div class="relative mt-2">
             {#if chatMessages.length > 0}
                <div class="absolute -top-3 left-0 bg-white border-2 border-black px-2 py-0.5 text-xs font-bold uppercase tracking-widest shadow z-10 text-black">
                  Conversation
                </div>
             {/if}
            <div class="flex flex-col gap-4 pt-6">
              {#each chatMessages as msg, i}
                <MessageBubble message={msg} {provider} index={i} />
              {/each}
            </div>
          </div>
        {:else}
          <div class="w-full h-32 flex items-center justify-center border-2 border-dashed border-gray-400 rounded-base bg-gray-50 text-gray-400 font-bold">
            No conversation messages found.
          </div>
        {/if}

      </div>

    {:else}
      <div class="relative h-full w-full pt-2">
        <button 
          class="absolute p-2 top-4 right-4 btn btn-sm bg-white border-2 border-black shadow-small z-20 hover:bg-slate-50 active:translate-y-[2px] active:shadow-none transition-all"
          onclick={copyJson}
          aria-label="Copy JSON"
        >
          {#if copied}
            <Check class="w-4 h-4 text-green-600"/>
          {:else}
            <Copy class="w-4 h-4" color="black"/>
          {/if}
        </button>
        
        <div class="h-full w-full rounded-base border-2 border-black overflow-auto bg-white p-1 text-xs">
           <div class="min-w-full min-h-full p-2">
             <CodeBlock lang="json" code={rawJson} showLineNumbers={true} />
          </div>
        </div>
      </div>
    {/if}

  </div>
</div>