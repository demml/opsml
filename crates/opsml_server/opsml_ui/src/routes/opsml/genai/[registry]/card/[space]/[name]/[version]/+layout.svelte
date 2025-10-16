<script lang="ts">
  import type { LayoutProps } from './$types';
  import ModelCardLayout from '$lib/components/card/layouts/ModelCardLayout.svelte';
  import DataCardLayout from '$lib/components/card/layouts/DataCardLayout.svelte';
  import ExperimentCardLayout from '$lib/components/card/layouts/ExperimentCardLayout.svelte';
  import ServiceCardLayout from '$lib/components/card/layouts/ServiceCardLayout.svelte';
  import type { RegistryType } from '$lib/utils';
  import PromptCardLayout from '$lib/components/card/layouts/PromptCardLayout.svelte';

  let { data, children }: LayoutProps = $props();

  /**
   * Map of registry types to their corresponding layout components
   * Provides type-safe dynamic component selection
   */
  const layoutComponents = {
    model: ModelCardLayout,
    data: DataCardLayout,
    experiment: ExperimentCardLayout,
    service: ServiceCardLayout,
    mcp: ServiceCardLayout,
    prompt: PromptCardLayout,
    // @ts-ignore
  } as const satisfies Record<RegistryType, any>;

  /**
   * Dynamically select the appropriate layout component based on registry type
   * Falls back to ModelCardLayout for unknown types to prevent runtime errors
   */
  const LayoutComponent = $derived(
    // @ts-ignore
    layoutComponents[data.registryType] ?? ModelCardLayout
  );
</script>

<!-- 
  Dynamic layout component selection based on registry type
  Each registry type (model, data, experiment, service) has its own specialized layout
  with appropriate navigation tabs and functionality
-->
<LayoutComponent metadata={data.metadata}  registryType={data.registryType}>
  {@render children()}
</LayoutComponent>