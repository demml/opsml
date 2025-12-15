<script lang="ts">
  import type { Snippet } from 'svelte';
  import { IdCard, FolderTree, Tag, Activity, Search } from 'lucide-svelte';
  import { page } from '$app/state';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import { dev } from '$app/environment';

  interface PromptMetadata {
    space: string;
    name: string;
    version: string;
    metadata: {
      drift_profile_uri_map?: any;
    };
  }

  interface PromptLayoutProps {
    metadata: PromptMetadata;
    registryType: string;
    children: Snippet;
  }

  let { metadata, registryType, children }: PromptLayoutProps = $props();

  /**
   * Determines the active tab based on the current URL path
   */
  let activeTab = $derived.by(() => {
    const last = page.url.pathname.split('/').pop() ?? '';
    if (['card', 'files', 'monitoring', 'observability', 'versions', 'view'].includes(last)) return last;
    return 'card';
  });

  /**
   * Determines if monitoring tab should be shown based on metadata and settings
   */
  let showMonitoring = $derived(
    (metadata.metadata.drift_profile_uri_map && uiSettingsStore.scouterEnabled) || dev
  );

  /**
   * Base path for navigation links
   */
  let basePath = $derived(
    `/opsml/genai/${registryType.toLowerCase()}/card/${metadata.space}/${metadata.name}/${metadata.version}`
  );

  const iconColor = '#8059b6';
</script>

<!-- Sticky header with breadcrumb and tab navigation -->
<div class="sticky top-14 z-10 flex-none pt-2 pb-1 border-b-2 border-black bg-surface-100">
  <div class="flex flex-col mx-auto justify-start px-4">
    <!-- Breadcrumb Navigation -->
    <h1 class="flex flex-row flex-wrap items-center">
      <div class="group flex flex-none items-center">
        <a
          class="font-semibold text-black hover:text-secondary-500 transition-colors"
          href={`/opsml/space/${metadata.space}`}
          aria-label={`Navigate to ${metadata.space} space`}
        >
          {metadata.space}
        </a>
        <div class="mx-0.5 text-gray-800" aria-hidden="true">/</div>
      </div>
      <div class="font-bold text-primary-800">
        <a
          href={basePath.replace(`/${metadata.version}`, '')}
          class="hover:text-primary-600 transition-colors"
          aria-label={`Navigate to ${metadata.name} prompt overview`}
        >
          {metadata.name}
        </a>
      </div>
      <div class="mx-0.5 text-gray-800" aria-hidden="true">/</div>
      <div class="font-semibold text-primary-800">{metadata.version}</div>
    </h1>

    <!-- Tab Navigation -->
    <nav class="flex flex-row gap-x-4 text-black pl-4 py-2 text-smd flex-wrap" aria-label="Prompt navigation">
      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'card' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
        href={`${basePath}/card`}
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'card' ? 'page' : undefined}
      >
        <IdCard color={iconColor} size={16} />
        <span>Card</span>
      </a>

      {#if showMonitoring}
        <a
          class="flex items-center gap-x-2 border-b-3 {activeTab === 'monitoring' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
          href={`${basePath}/monitoring`}
          data-sveltekit-preload-data="hover"
          aria-current={activeTab === 'monitoring' ? 'page' : undefined}
        >
          <Activity color={iconColor} size={16} />
          <span>Monitoring</span>
        </a>
      {/if}

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'observability' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3"
        href={`${basePath}/observability`}
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'observability' ? 'page' : undefined}
      >
        <Search color="#8059b6" size={16} />
        <span>Observability</span>
      </a>

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'files' || activeTab === 'view' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
        href={`${basePath}/files`}
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'files' || activeTab === 'view' ? 'page' : undefined}
      >
        <FolderTree color={iconColor} size={16} />
        <span>Files</span>
      </a>

      <a
        class="flex items-center gap-x-2 border-b-3 {activeTab === 'versions' ? 'border-secondary-500' : 'border-transparent'} hover:border-secondary-500 hover:border-b-3 transition-colors"
        href={`${basePath}/versions`}
        data-sveltekit-preload-data="hover"
        aria-current={activeTab === 'versions' ? 'page' : undefined}
      >
        <Tag color={iconColor} fill={iconColor} size={16} />
        <span>Versions</span>
      </a>
    </nav>
  </div>
</div>

<main aria-label="Prompt content">
  {@render children()}
</main>