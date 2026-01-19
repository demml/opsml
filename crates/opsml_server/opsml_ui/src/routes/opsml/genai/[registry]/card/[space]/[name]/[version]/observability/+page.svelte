<script lang="ts">

  import TraceDetailContent from '$lib/components/trace/TraceDetailContent.svelte';
  import type { PageProps } from './$types';
  import type { TraceListItem } from '$lib/components/trace/types';
  import type {  TraceSpansResponse } from "$lib/components/trace/types";
  import NoTraceView from "$lib/components/trace/NoTraceView.svelte";
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from "$lib/components/scouter/ScouterRequiredView.svelte";
  import { Search } from 'lucide-svelte';


  let { data }: PageProps = $props();
  let trace: TraceListItem | null = $state(data.trace);
  let traceSpans: TraceSpansResponse | null  = $state(data.spans);
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);

</script>

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  {#if scouterEnabled}
    {#if trace && traceSpans}
      <div class="border-black border-2 rounded-lg shadow">
        <TraceDetailContent
          trace={trace}
          traceSpans={traceSpans}
          showCloseButton={false}
        />
      </div>
    {:else}
      <NoTraceView message={data.errorMessage} type={data.type} />
    {/if}
  {:else}
    <ScouterRequiredView
      featureName="Observability Dashboard"
      featureDescription="Track distributed traces, monitor request flows, and identify performance bottlenecks across your services with real-time observability powered by Scouter."
      icon={Search}
    />
  {/if}
</div>

