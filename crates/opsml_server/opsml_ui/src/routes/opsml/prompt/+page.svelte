<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { Code, Files } from 'lucide-svelte';

  function getLastPartOfPath(path: string): string {
    const parts = path.split("/");
    return parts[parts.length - 1];
  }


  let { data }: PageProps = $props();
  let registry_page:  RegistryPageReturn  = data.page;
  let selectedSpace: string | undefined = data.selectedSpace;
  let selectedName: string | undefined = data.selectedName;

  let activeTab = $state(getLastPartOfPath(page.url.pathname));

  function navigateTab(tab: string) {
    if (activeTab === tab) {
      return;
    }

    activeTab = tab;

    const registryType = registry_page.registry_type.toLowerCase();

    if (activeTab === 'prompt') {
      goto(`/opsml/${registryType}`);
      return; // Ensure no further navigation happens
    }

    goto(`/opsml/${registryType}/${activeTab}`);
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
      <CardsSearch 
        selectedSpace={selectedSpace}
        selectedName={selectedName}
        page={registry_page}
        title={registry_page.registry_type}
      />
    </div>
  </div>
</div>