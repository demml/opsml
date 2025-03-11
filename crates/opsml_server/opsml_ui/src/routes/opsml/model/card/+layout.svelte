<script lang="ts">
  import { onMount } from 'svelte';
  import type { LayoutProps } from './$types';
  import { getRegistryTypeLowerCase } from '$lib/utils';
  import { IdCard, FolderTree, Activity, Tag } from 'lucide-svelte';

  let { data, children }: LayoutProps = $props();

  let activeTab = $state('card');

  let repository = data.metadata.repository;
  let name = data.metadata.name;
  let version = data.metadata.version;
  let registry = $state('');
  let group = $state('card');


  onMount(() => {
      registry = getRegistryTypeLowerCase(data.registry);
  });

</script>

<div class="min-h-screen">
  <div class="pt-20 m500:pt-14 lg:pt-[100px] border-b bg-slate-50">
    <div class="flex flex-col mx-auto flex w-11/12 justify-start">
      <h1 class="flex flex-row flex-wrap items-center text-xl">
        <div class="group flex flex-none items-center">
          <a class="font-semibold text-black hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
          <div class="mx-0.5 text-gray-800">/</div>
        </div>
        <div class="font-bold text-primary-700">{name}</div>
        <div class="mx-0.5 text-gray-800">/</div>
        <div class="font-semibold text-primary-700">{version}</div>
      </h1>

      <div class="flex flex-row gap-x-8 text-black text-lg pl-4 h-10 mb-2">

        <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'card' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => activeTab = 'card'}>
          <IdCard color="#8059b6"/>
          <span>Card</span>
        </button>
        <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'files' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => activeTab = 'files'}>
          <FolderTree color="#8059b6"/>
          <span>Files</span>
        </button>
        <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'monitoring' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => activeTab = 'monitoring'}>
          <Activity color="#8059b6"/>
          <span>Monitoring</span>
        </button>
        <button class="flex items-center gap-x-2 border-b-3 {activeTab === 'versions' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3" onclick={() => activeTab = 'versions'}>
          <Tag color="#8059b6" fill="#8059b6"/>
          <span>Versions</span>
        </button>
      </div>



    </div>
  </div>
  {@render children()}
</div>
