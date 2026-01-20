<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag, Search, Activity } from 'lucide-svelte';
  import { page } from '$app/state';
  import { dev } from '$app/environment';
  import { getRegistryPath } from '$lib/utils';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import type { RegistryType } from '$lib/utils';

  interface ServiceMetadata {
    space: string;
    name: string;
    version: string;
  }

  interface ServiceLayoutProps {
    metadata: ServiceMetadata;
    registryType: RegistryType;
    has_drift_profile: boolean;
    children: Snippet;
  }

  let { metadata, registryType, has_drift_profile,children }: ServiceLayoutProps = $props();

  let scouterEnabled: boolean = $state(uiSettingsStore.scouterEnabled);

  /**
   * Determines the active tab based on the current URL path
   * Service-specific tabs: card, files, versions (minimal set for service management)
   */
  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'monitoring','observability', 'versions', 'view'].includes(last)) return last;
    return 'card';
  });

  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );

  let showMonitoring = $derived(
    (has_drift_profile && scouterEnabled) || dev
  );

  /**
   * Navigation configuration for service-specific tabs
   * Minimal set focused on service deployment and management essentials
   */
  const navItems = $derived.by(() => {
    const baseItems = [
      {
        key: 'card' as const,
        label: 'Card',
        icon: IdCard,
        isActive: (tab: string): tab is 'card' => tab === 'card',
        description: 'Service details and configuration'
      },
      {
        key: 'files' as const,
        label: 'Files',
        icon: FolderTree,
        isActive: (tab: string): tab is 'files' | 'view' => tab === 'files' || tab === 'view',
        description: 'Service artifacts and deployment files'
      },
      {
        key: 'observability' as const,
        label: 'Observability',
        icon: Search,
        isActive: (tab: string): tab is 'observability' => tab === 'observability',
        description: 'Service observability and monitoring'
      },
      {
        key: 'versions' as const,
        label: 'Versions',
        icon: Tag,
        isActive: (tab: string): tab is 'versions' => tab === 'versions',
        iconProps: { fill: '#8059b6' },
        description: 'Service version history and releases'
      }
    ];

    if (showMonitoring) {
      baseItems.splice(2, 0, {
        // @ts-ignore
        key: 'service_monitoring' as const,
        label: 'Monitoring',
        icon: Activity,
        // @ts-ignore
        isActive: (tab: string): tab is 'monitoring' => tab === 'monitoring',
        description: 'Service performance and health monitoring'
      });
    }

    return baseItems;
  });

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
          class="flex items-center gap-x-2 border-b-3 {isActive ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
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