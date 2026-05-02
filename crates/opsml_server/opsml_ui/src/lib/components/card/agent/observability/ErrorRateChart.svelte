<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildErrorRateChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();
</script>

<GenAiChartCard title="Error Rate" subtitle="% per bucket" height="h-40" configFn={() => buildErrorRateChart(buckets)} />
