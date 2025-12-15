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

<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="border-2 border-black rounded-lg shadow overflow-hidden">
    <div class="flex flex-col">
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
  </div>
</div>