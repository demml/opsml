<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag, Activity, ChartColumnDecreasing, ChartArea } from 'lucide-svelte';
  import { page } from '$app/state';
  import { getRegistryPath } from '$lib/utils';
  import type { RegistryType } from '$lib/utils';

  interface ExperimentMetadata {
    space: string;
    name: string;
    version: string;
  }

  interface ExperimentLayoutProps {
    metadata: ExperimentMetadata;
    registryType: RegistryType;
    children: Snippet;
  }

  let { metadata, registryType, children }: ExperimentLayoutProps = $props();

  /**
   * Determines the active tab based on the current URL path
   * Experiment-specific tabs: card, files, metrics, figures, hardware, versions, view
   */
  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'metrics', 'hardware', 'versions', 'figures', 'view'].includes(last)) return last;
    return 'card';
  });

  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );

  /**
   * Navigation configuration for experiment-specific tabs
   */
  const navItems = [
    {
      key: 'card',
      label: 'Card',
      icon: IdCard,
      path: `${basePath}/card`,
      isActive: (tab: string) => tab === 'card',
      description: 'Experiment overview and details'
    },
    {
      key: 'files',
      label: 'Files',
      icon: FolderTree,
      path: `${basePath}/files`,
      isActive: (tab: string) => tab === 'files' || tab === 'view',
      description: 'Experiment artifacts and outputs'
    },
    {
      key: 'metrics',
      label: 'Metrics',
      icon: ChartColumnDecreasing,
      path: `${basePath}/metrics`,
      isActive: (tab: string) => tab === 'metrics',
      description: 'Performance metrics and KPIs'
    },
    {
      key: 'figures',
      label: 'Figures',
      icon: ChartArea,
      path: `${basePath}/figures`,
      isActive: (tab: string) => tab === 'figures',
      description: 'Charts, plots, and visualizations'
    },
    {
      key: 'hardware',
      label: 'Hardware',
      icon: Activity,
      path: `${basePath}/hardware`,
      isActive: (tab: string) => tab === 'hardware',
      description: 'System resource usage and monitoring'
    },
    {
      key: 'versions',
      label: 'Versions',
      icon: Tag,
      path: `${basePath}/versions`,
      isActive: (tab: string) => tab === 'versions',
      iconProps: { fill: '#8059b6' },
      description: 'Version history and comparisons'
    }
  ];

  /**
   * Primary color for consistent icon styling
   */
  const iconColor = '#8059b6';
</script>

<div class="sticky top-14 z-10 flex-none pt-2 pb-1 border-b-2 border-black bg-surface-100">
  <div class="flex flex-col mx-auto justify-start px-4">
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
          aria-label="Navigate to {metadata.name} experiment overview"
        >
          {metadata.name}
        </a>
      </div>
      <div class="mx-0.5 text-gray-800" aria-hidden="true">/</div>
      <div class="font-semibold text-primary-800">{metadata.version}</div>
    </h1>

    <nav 
      class="flex flex-row gap-x-4 text-black pl-4 py-2 text-smd flex-wrap" 
      aria-label="Experiment navigation"
      role="tablist"
    >
      {#each navItems as item}
        {@const isActive = item.isActive(activeTab)}
        <a
          class="flex items-center gap-x-2 border-b-3 {isActive ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2 rounded-t"
          href={item.path}
          data-sveltekit-preload-data="hover"
          aria-current={isActive ? 'page' : undefined}
          role="tab"
          aria-selected={isActive}
          title={item.description}
        >
          <svelte:component 
            this={item.icon} 
            color={iconColor} 
            size={16} 
            {...(item.iconProps || {})}
          />
          <span>{item.label}</span>
        </a>
      {/each}
    </nav>
  </div>
</div>

<main role="main" aria-label="Experiment content">
  {@render children()}
</main>