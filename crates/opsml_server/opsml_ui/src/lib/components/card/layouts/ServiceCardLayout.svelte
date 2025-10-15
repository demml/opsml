<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag } from 'lucide-svelte';
  import { page } from '$app/state';
  import { getRegistryPath } from '$lib/utils';
  import type { RegistryType } from '$lib/utils';

  interface ServiceMetadata {
    space: string;
    name: string;
    version: string;
  }

  interface ServiceLayoutProps {
    metadata: ServiceMetadata;
    registryType: RegistryType;
    children: Snippet;
  }

  let { metadata, registryType, children }: ServiceLayoutProps = $props();

  /**
   * Determines the active tab based on the current URL path
   * Service-specific tabs: card, files, versions (minimal set for service management)
   */
  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'versions'].includes(last)) return last;
    return 'card';
  });

  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );

  /**
   * Navigation configuration for service-specific tabs
   * Minimal set focused on service deployment and management essentials
   */
  const navItems = [
    {
      key: 'card',
      label: 'Card',
      icon: IdCard,
      isActive: (tab: string) => tab === 'card',
      description: 'Service details and configuration'
    },
    {
      key: 'files',
      label: 'Files',
      icon: FolderTree,
      isActive: (tab: string) => tab === 'files',
      description: 'Service artifacts and deployment files'
    },
    {
      key: 'versions',
      label: 'Versions',
      icon: Tag,
      isActive: (tab: string) => tab === 'versions',
      iconProps: { fill: '#8059b6' },
      description: 'Service version history and releases'
    }
  ];

  const iconColor = '#8059b6';
</script>

<!-- Service Header with sticky navigation -->
<div class="sticky top-14 z-10 flex-none pt-2 pb-1 border-b-2 border-black bg-surface-100">
  <div class="flex flex-col mx-auto justify-start px-4">
    <!-- Breadcrumb Navigation -->
    <h1 class="flex flex-row flex-wrap items-center">
      <div class="group flex flex-none items-center">
        <a 
          class="font-semibold text-black hover:text-secondary-500 transition-colors" 
          href="/opsml/space/{metadata.space}"
          aria-label="Navigate to {metadata.space} space"
        >
          {metadata.space}
        </a>
        <div class="mx-0.5 text-gray-800" aria-hidden="true">/</div>
      </div>
      <div class="font-bold text-primary-800">
        <a 
          href="{basePath.replace(`/${metadata.version}`, '')}"
          class="hover:text-primary-600 transition-colors"
          aria-label="Navigate to {metadata.name} service overview"
        >
          {metadata.name}
        </a>
      </div>
      <div class="mx-0.5 text-gray-800" aria-hidden="true">/</div>
      <div class="font-semibold text-primary-800">{metadata.version}</div>
    </h1>

    <!-- Tab Navigation -->
    <nav 
      class="flex flex-row gap-x-4 text-black pl-4 py-2 text-smd flex-wrap" 
      aria-label="Service navigation"
    >
      {#each navItems as item}
        {@const isActive = item.isActive(activeTab)}
        <a
          href={`${basePath}/${item.key}`}
          class="flex items-center gap-x-2 border-b-3 {isActive ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2 rounded-t"
          data-sveltekit-preload-data="hover"
          aria-current={isActive ? 'page' : undefined}
          title={item.description}
        >
          <item.icon color={iconColor} size={16} {...(item.iconProps || {})} />
          <span>{item.label}</span>
        </a>
      {/each}
    </nav>
  </div>
</div>

<main aria-label="Service content">
  {@render children()}
</main>