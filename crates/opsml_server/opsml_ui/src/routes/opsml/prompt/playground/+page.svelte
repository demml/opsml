<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { Code, Files } from 'lucide-svelte';
  import Pill from "$lib/components/utils/Pill.svelte";
  import { type Message, type MessageRole } from "$lib/components/card/prompt/types";
  import { fade } from 'svelte/transition';
  import PromptMessage from "$lib/components/card/prompt/PromptMessage.svelte";

  function getLastPartOfPath(path: string): string {
    const parts = path.split("/");
    return parts[parts.length - 1];
  }


  let { data }: PageProps = $props();

  let activeTab = $state(getLastPartOfPath(page.url.pathname));
  let messages = $state<Message[]>([]);
  let showRoleSelector = $state(false);

  function addMessage(role: MessageRole) {
    const newMessage: Message = {
      content: { Str: '' },
      next_param: messages.length,
      role: role
    };
    messages = [...messages, newMessage];
    showRoleSelector = false;
  }

  function navigateTab(tab: string) {
    if (activeTab === tab) {
      return;
    }

    activeTab = tab;

    const registryType = data.registry_type.toLowerCase();

    if (activeTab === 'prompt') {
      goto(`/opsml/${registryType}`);
      return; // Ensure no further navigation happens
    }

    goto(`/opsml/${registryType}/${activeTab}`);
  }

  function deleteMessage(index: number) {
    messages = messages.filter((_, i) => i !== index);
  }


</script>

<div class="h-screen flex flex-col bg-surface-50">
  <div class="flex-1 overflow-auto">

    <div class="flex-none pt-20 m500:pt-14 lg:pt-[85px] border-b-2 border-black bg-slate-100">
      <div class="flex flex-col mx-auto flex w-11/12 justify-start">

  
        <div class="flex flex-row gap-x-8 text-black text-lg pl-4 h-10 mb-2">

          <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'prompt' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => navigateTab('prompt')}>
            <Files color="#8059b6"/>
            <span>Cards</span>
          </button>
  
  
          <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'playground' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => navigateTab('playground')}>
            <Code color="#8059b6"/>
            <span>Playground</span>
          </button>

  
        </div>
  
  
  
      </div>
    </div>


    <div class="mx-auto w-9/12 pt-4 pb-10 flex justify-center px-4">

      <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">

        <div class="col-span-1 md:col-span-4 bg-white p-4 flex flex-col rounded-base border-black border-2 shadow min-h-[400px]">
          
          <div class="flex-1 overflow-y-auto">
            <div class="flex flex-col items-start justify-start">
              {#if messages.length === 0}
                <div class="flex flex-col items-center justify-center h-[300px] w-full gap-4">
                  <div class="text-center text-primary-800 text-xl font-bold text-black">No Messages</div>
                  <div class="text-center text-lg font-bold text-black">Click below to add messages to the prompt</div>
                </div>
              {:else}
                {#each messages as message, index (index)}
                  <PromptMessage message={message} deleteCallback={() => deleteMessage(index)}/>
                {/each}
              {/if}
            </div>
          </div>

          <div class="mt-auto pt-4 flex justify-center relative">
            {#if showRoleSelector}
              <div 
                class="absolute bottom-12 bg-white border-2 border-black rounded-lg shadow-lg p-2 flex flex-col gap-2"
                transition:fade
              >
                <button
                  class="px-4 py-2 text-black bg-primary-200 rounded hover:bg-primary-500"
                  onclick={() => addMessage('system')}
                >
                  System
                </button>
                <button
                  class="px-4 py-2 text-black bg-secondary-300 rounded hover:bg-secondary-500"
                  onclick={() => addMessage('user')}
                >
                  User
                </button>
              </div>
            {/if}
            <button 
              class="text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 px-4 w-38 h-10"
              onclick={() => showRoleSelector = !showRoleSelector}
            >
              {showRoleSelector ? 'Cancel' : 'Add Message'}
            </button>
          </div>
          


        </div>

        <div class="col-span-1 md:col-span-2 bg-white p-4 flex flex-col rounded-base border-black border-2 shadow h-[400px]">
          <h2 class="font-bold text-primary-800 text-xl pb-3">Provider Settings</h2>
        </div>
      </div>
      
    </div>
  </div>
</div>