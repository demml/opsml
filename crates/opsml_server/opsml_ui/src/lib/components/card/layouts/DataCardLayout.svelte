<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag, BookOpenText } from 'lucide-svelte';
  import { page } from '$app/state';
  import { getRegistryPath } from '$lib/utils';
  import type { RegistryType } from '$lib/utils';

  interface DataMetadata {
    space: string;
    name: string;
    version: string;
  }

  interface DataLayoutProps {
    metadata: DataMetadata;
    registryType: RegistryType;
    children: Snippet;
  }

  let { metadata, registryType, children }: DataLayoutProps = $props();

  /**
   * Determines the active tab based on the current URL path
   * Data-specific tabs: card, files, profile, versions, view
   */
  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'profile', 'versions', 'view'].includes(last)) return last;
    return 'card';
  });

  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );

  /**
   * Navigation configuration for data-specific tabs
   */
  const navItems = [
    {
      key: 'card',
      label: 'Card',
      icon: IdCard,
      path: `${basePath}/card`,
      isActive: (tab: string) => tab === 'card'
    },
    {
      key: 'files',
      label: 'Files',
      icon: FolderTree,
      path: `${basePath}/files`,
      isActive: (tab: string) => tab === 'files' || tab === 'view'
    },
    {
      key: 'profile',
      label: 'Profile',
      icon: BookOpenText,
      path: `${basePath}/profile`,
      isActive: (tab: string) => tab === 'profile'
    },
    {
      key: 'versions',
      label: 'Versions',
      icon: Tag,
      path: `${basePath}/versions`,
      isActive: (tab: string) => tab === 'versions',
      iconProps: { fill: '#8059b6' }
    }
  ];
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

    <nav class="flex flex-row gap-x-4 text-black pl-4 py-2 text-smd flex-wrap" aria-label="Data navigation">
      {#each navItems as item}
        {@const isActive = item.isActive(activeTab)}
        <a
          class="flex items-center gap-x-2 border-b-3 {isActive ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
          href={item.path}
          data-sveltekit-preload-data="hover"
          aria-current={isActive ? 'page' : undefined}
        >
          <svelte:component 
            this={item.icon} 
            color="#8059b6" 
            size={16} 
            {...(item.iconProps || {})}
          />
          <span>{item.label}</span>
        </a>
      {/each}
    </nav>
  </div>
</div>

<main>
  {@render children()}
</main>