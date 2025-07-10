<script lang="ts">
  import { onMount } from 'svelte';
  import type { LayoutProps } from './$types';
  import { getRegistryTypeLowerCase } from '$lib/utils';
  import { IdCard, FolderTree, Activity, Tag } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { uiSettingsStore } from "$lib/components/settings/settings.svelte";


  function navigateTab(tab: string) {
    if (data.activeTab === tab) {
      return;
    }
    data.activeTab = tab;
    goto(`/opsml/${registry}/card/${data.activeTab}?space=${data.metadata.space}&name=${data.metadata.name}&version=${data.metadata.version}`);
  };

  let { data, children }: LayoutProps = $props();

  let registry = $state('');

  // Make these reactive by accessing data.metadata directly
  $effect(() => {
    registry = getRegistryTypeLowerCase(data.registry);
  });

</script>


<div class="h-screen flex flex-col">
  <div class="flex-none pt-16 pb-1 border-b-2 border-black bg-slate-100">
    <div class="flex flex-col mx-auto flex w-11/12 justify-start">
      <h1 class="flex flex-row flex-wrap items-center">
        <div class="group flex flex-none items-center">
          <a class="font-semibold text-black hover:text-secondary-500" href="/opsml/{registry}?space={data.metadata.space}">{data.metadata.space}</a>
          <div class="mx-0.5 text-gray-800">/</div>
        </div>
        <div class="font-bold text-primary-800">{data.metadata.name}</div>
        <div class="mx-0.5 text-gray-800">/</div>
        <div class="font-semibold text-primary-800">{data.metadata.version}</div>
      </h1>

      <div class="flex flex-row gap-x-4 text-black pl-4 h-8 mb-1 text-smd">

        <button class="flex items-center gap-x-2 border-b-3 {data.activeTab === 'home' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => navigateTab('home')}>
          <IdCard color="#8059b6"/>
          <span>Card</span>
        </button>
        <button class="flex items-center gap-x-2 border-b-3 {data.activeTab === 'files' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => navigateTab('files')}>
          <FolderTree color="#8059b6"/>
          <span>Files</span>
        </button>

        <button class="flex items-center gap-x-2 border-b-3 {data.activeTab === 'versions' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => navigateTab('versions')}>
          <Tag color="#8059b6" fill="#8059b6"/>
          <span>Versions</span>
        </button>
      </div>



    </div>
  </div>
  <div class="flex-1 overflow-auto">
    {@render children()}
  </div>
</div>
