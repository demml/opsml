<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildTokenChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();
</script>

<GenAiChartCard title="Tokens" subtitle="in · out · cache" height="h-40" configFn={() => buildTokenChart(buckets)} />
