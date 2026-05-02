<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildLatencyChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();
</script>

<GenAiChartCard title="Latency" subtitle="p50 · p95 · p99" height="h-40" configFn={() => buildLatencyChart(buckets)} />
