<script lang="ts">
  import type { LayoutProps } from './$types';
  import { IdCard, FolderTree, Tag, Activity } from 'lucide-svelte';
  import { page } from '$app/state';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import { getRegistryPath } from '$lib/utils';

  let { data, children }: LayoutProps = $props();


  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'monitoring', 'versions', 'view'].includes(last)) return last;
    return 'card';
  });

</script>

<div class="h-screen flex flex-col">
  <div class="sticky top-0 z-10 flex-none pt-2 pb-1 border-b-2 border-black bg-surface-100">
    <div class="flex flex-col mx-auto justify-start px-4">
      <h1 class="flex flex-row flex-wrap items-center">
        <div class="group flex flex-none items-center">
          <a class="font-semibold text-black hover:text-secondary-500" href="/opsml/space/{data.metadata.space}">{data.metadata.space}</a>
          <div class="mx-0.5 text-gray-800">/</div>
        </div>
        <div class="font-bold text-primary-800">
          <a href={`/opsml/${getRegistryPath(data.registryType)}/card/${data.metadata.space}/${data.metadata.name}`}>
          {data.metadata.name}
          </a>
        </div>
        <div class="mx-0.5 text-gray-800">/</div>
        <div class="font-semibold text-primary-800">{data.metadata.version}</div>
      </h1>

      <div class="flex flex-row gap-x-4 text-black pl-4 h-8 mb-1 text-smd">
        <a
          class="flex items-center gap-x-2 border-b-3 {activeTab === 'card' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
          href={`/opsml/${getRegistryPath(data.registryType)}/card/${data.metadata.space}/${data.metadata.name}/${data.metadata.version}/card`}
          data-sveltekit-preload-data="hover"
        >
          <IdCard color="#8059b6"/>
          <span>Card</span>
        </a>
        <a
          class="flex items-center gap-x-2 border-b-3 {activeTab === 'files' || activeTab === 'view' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
          href={`/opsml/${getRegistryPath(data.registryType)}/card/${data.metadata.space}/${data.metadata.name}/${data.metadata.version}/files`}
          data-sveltekit-preload-data="hover"
        >
          <FolderTree color="#8059b6"/>
          <span>Files</span>
        </a>
        {#if data.metadata.metadata.interface_metadata.save_metadata.drift_profile_uri_map && uiSettingsStore.scouterEnabled}
          <a
            class="flex items-center gap-x-2 border-b-3 {activeTab === 'monitoring' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
            href={`/opsml/${getRegistryPath(data.registryType)}/card/${data.metadata.space}/${data.metadata.name}/${data.metadata.version}/monitoring`}
            data-sveltekit-preload-data="hover"
          >
            <Activity color="#8059b6"/>
            <span>Monitoring</span>
          </a>
        {/if}
        <a
          class="flex items-center gap-x-2 border-b-3 {activeTab === 'versions' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
          href={`/opsml/${getRegistryPath(data.registryType)}/card/${data.metadata.space}/${data.metadata.name}/${data.metadata.version}/versions`}
          data-sveltekit-preload-data="hover"
        >
          <Tag color="#8059b6" fill="#8059b6"/>
          <span>Versions</span>
        </a>
      </div>
    </div>
  </div>

  <!-- Child Content -->
  <div class="flex-1 overflow-auto">
    {@render children()}
  </div>
</div>