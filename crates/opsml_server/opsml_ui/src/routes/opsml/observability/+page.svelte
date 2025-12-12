<script lang="ts">
  import TraceDashboard from "$lib/components/trace/TraceDashboard.svelte";
  import TraceErrorView from "$lib/components/trace/TraceErrorView.svelte";
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

</script>

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