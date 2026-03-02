<script lang="ts">
  import type { LayoutProps } from './$types';
  import ModelCardLayout from '$lib/components/card/layouts/ModelCardLayout.svelte';
  import DataCardLayout from '$lib/components/card/layouts/DataCardLayout.svelte';
  import ExperimentCardLayout from '$lib/components/card/layouts/ExperimentCardLayout.svelte';
  import ServiceCardLayout from '$lib/components/card/layouts/ServiceCardLayout.svelte';
  import type { RegistryType } from '$lib/utils';
  import PromptCardLayout from '$lib/components/card/layouts/PromptCardLayout.svelte';
  import type { Component } from 'svelte';

  let { data, children }: LayoutProps = $props();

  /**
   * Map of registry types to their corresponding layout components
   * Provides type-safe dynamic component selection
   */
  const layouts: Record<RegistryType, Component<any>> = {
    model: ModelCardLayout,
    data: DataCardLayout,
    experiment: ExperimentCardLayout,
    service: ServiceCardLayout,
    mcp: ServiceCardLayout,
    prompt: PromptCardLayout,
    agent: ServiceCardLayout
  };

  // Derive the component based on the registryType from Rust API data
  const SelectedLayout = $derived(layouts[data.registryType] ?? ModelCardLayout);

</script>

<!--
  Dynamic layout component selection based on registry type
  Each registry type (model, data, experiment, service) has its own specialized layout
  with appropriate navigation tabs and functionality
-->

{#if data.metadata}
  <SelectedLayout
    data={data}
    registryType={data.registryType}
  >
    {@render children()}
  </SelectedLayout>
{/if}