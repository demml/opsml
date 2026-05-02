<script lang="ts">
  import TraceDetailIntegrationMock from '$lib/components/dev/agentMetricsMocks/TraceDetailIntegrationMock.svelte';
  import { buildTraceMockResponse } from '$lib/components/dev/agentMetricsMocks/traceMockData';
  import { buildTraceListItem, buildTraceSpansResponse } from '$lib/components/dev/agentMetricsMocks/traceAdapter';

  const genAiData = buildTraceMockResponse();
  const traceItem = buildTraceListItem(genAiData);
  const traceSpans = buildTraceSpansResponse(genAiData);
</script>

<div class="h-screen overflow-hidden">
  <TraceDetailIntegrationMock {genAiData} {traceItem} {traceSpans} />
</div>
