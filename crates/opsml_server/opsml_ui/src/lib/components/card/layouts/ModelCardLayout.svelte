<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag, Activity, Search } from 'lucide-svelte';
  import { page } from '$app/state';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import { getRegistryPath } from '$lib/utils';
  import { dev } from '$app/environment';
  import type { RegistryType } from '$lib/utils';

  interface CardMetadata {
    space: string;
    name: string;
    version: string;
    metadata: {
      interface_metadata: {
        save_metadata: {
          drift_profile_uri_map?: any;
        };
      };
    };
  }

  interface CardLayoutProps {
    metadata: CardMetadata;
    registryType: RegistryType;
    has_drift_profile: boolean;
    children: Snippet;
  }

  let { metadata, registryType, has_drift_profile, children }: CardLayoutProps = $props();

  let scouterEnabled: boolean = $state(uiSettingsStore.scouterEnabled);

  /**
   * Determines the active tab based on the current URL path
   */
  let activeTab = $derived.by(() => {
    const pathParts = page.url.pathname.split('/');
    const last = pathParts[pathParts.length - 1] ?? '';
    const secondLast = pathParts[pathParts.length - 2] ?? '';
    
    // Check if we're in a nested monitoring route
    if (secondLast === 'monitoring') return 'monitoring';
    
    // Direct routes
    if (['card', 'files', 'monitoring', 'versions', 'view', 'observability'].includes(last)) return last;
    
    return 'card';
  });

  /**
   * Determines if monitoring tab should be shown based on metadata and settings
   */
  let showMonitoring = $derived(
    (has_drift_profile && scouterEnabled) || dev
  );


  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );
</script>

<div class="sticky top-14 z-10 flex-none pt-2 pb-1 border-b-2 border-black bg-surface-100">
  <div class="flex flex-col mx-auto justify-start px-4">
    <h1 class="flex flex-row flex-wrap items-center">
      <div class="group flex flex-none items-center">
        <a
          class="font-semibold text-black hover:text-secondary-500" 
          href="/opsml/space/{metadata.space}"
        >
          {metadata.space}
        </a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-800">
        <a href="{basePath.replace(`/${metadata.version}`, '')}">
          {metadata.name}
        </a>
      </div>
      <div class="mx-0.5 text-gray-800">/</div>
      <div class="font-semibold text-primary-800">{metadata.version}</div>
    </h1>

    <nav class="flex flex-row gap-x-4 text-black pl-4 py-2 text-smd flex-wrap" aria-label="Card navigation">
      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'card' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
        href="{basePath}/card"
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'card' ? 'page' : undefined}
      >
        <IdCard color="#8059b6" size={16} />
        <span>Card</span>
      </a>

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'files' || activeTab === 'view' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
        href="{basePath}/files"
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'files' || activeTab === 'view' ? 'page' : undefined}
      >
        <FolderTree color="#8059b6" size={16} />
        <span>Files</span>
      </a>

      {#if showMonitoring}
        <a
          class="flex items-center gap-x-2 border-b-3 {activeTab === 'monitoring' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
          href="{basePath}/monitoring"
          data-sveltekit-preload-data="hover"
          aria-current={activeTab === 'monitoring' ? 'page' : undefined}
        >
          <Activity color="#8059b6" size={16} />
          <span>Monitoring</span>
        </a>
      {/if}

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'observability' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
        href="{basePath}/observability"
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'observability' ? 'page' : undefined}
      >
        <Search color="#8059b6" size={16} />
        <span>Observability</span>
      </a>

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'versions' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
        href="{basePath}/versions"
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'versions' ? 'page' : undefined}
      >
        <Tag color="#8059b6" fill="#8059b6" size={16} />
        <span>Versions</span>
      </a>
    </nav>
  </div>
</div>

<main>
  {@render children()}
</main>