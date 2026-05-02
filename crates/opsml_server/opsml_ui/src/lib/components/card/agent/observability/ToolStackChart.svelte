<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildToolStackChart } from './charts';
  import type { ToolTimeBucket } from './types';

  let { series }: { series: ToolTimeBucket[] } = $props();

  const cfg = $derived(() => buildToolStackChart(series));
</script>

<GenAiChartCard title="Tool Calls" subtitle="stacked" height="h-40" configFn={cfg} />
