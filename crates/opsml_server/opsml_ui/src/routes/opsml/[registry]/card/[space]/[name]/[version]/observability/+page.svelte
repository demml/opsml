<script lang="ts">

  import TraceDetailContent from '$lib/components/trace/TraceDetailContent.svelte';
  import type { PageProps } from './$types';
  import type { TraceListItem } from '$lib/components/trace/types';
  import type {  TraceSpansResponse } from "$lib/components/trace/types";
  import NoTraceView from "$lib/components/trace/NoTraceView.svelte";

  let { data }: PageProps = $props();
  let trace: TraceListItem | null = $state(data.trace);
  let traceSpans: TraceSpansResponse | null  = $state(data.spans);

</script>

<div class="mx-auto max-w-8xl pb-8 px-4">
  {#if trace && traceSpans}
    <TraceDetailContent
      trace={trace}
      traceSpans={traceSpans}
      showCloseButton={false}
    />
  {:else}
    <NoTraceView message={data.errorMessage} type={data.type} />
  {/if}
</div>