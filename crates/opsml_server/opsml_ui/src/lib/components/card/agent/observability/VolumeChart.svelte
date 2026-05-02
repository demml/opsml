<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildVolumeChart } from './charts';
  import type { AgentMetricBucket } from './types';

  let { buckets }: { buckets: AgentMetricBucket[] } = $props();

  const cfg = $derived(() => buildVolumeChart(buckets));
</script>

<GenAiChartCard title="Volume" subtitle="success · err" height="h-40" configFn={cfg} />
