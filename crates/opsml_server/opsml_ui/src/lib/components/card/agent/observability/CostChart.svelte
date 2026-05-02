<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildCostChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();
</script>

<GenAiChartCard title="Cost" subtitle="$ / bucket" height="h-40" configFn={() => buildCostChart(buckets)} />
