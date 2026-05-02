<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildLatencyChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();

  const cfg = $derived(() => buildLatencyChart(buckets));
</script>

<GenAiChartCard title="Latency" subtitle="p50 · p95 · p99" height="h-40" configFn={cfg} />
