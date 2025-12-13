<script lang="ts">
  import TraceDashboard from "$lib/components/trace/TraceDashboard.svelte";
  import TraceErrorView from "$lib/components/trace/TraceErrorView.svelte";
  import ScouterRequiredView from "$lib/components/scouter/ScouterRequiredView.svelte";
  import { Activity } from 'lucide-svelte';
  import type { PageProps } from './$types';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';

  let { data }: PageProps = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
</script>

{#if scouterEnabled}
  {#if data.status === 'error' || data.status === 'not_found'}
    <TraceErrorView
      message={data.errorMessage}
      type={data.status}
      initialFilters={data.initialFilters}
    />
  {:else}
    <TraceDashboard
      trace_page={data.trace_page}
      trace_metrics={data.trace_metrics.metrics}
      initialFilters={data.initialFilters}
    />
  {/if}
{:else}
  <ScouterRequiredView
    featureName="Observability Dashboard"
    featureDescription="Track distributed traces, monitor request flows, and identify performance bottlenecks across your services with real-time observability powered by Scouter."
    icon={Activity}
  />
{/if}