<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildToolStackChart } from './charts';
  import type { ToolTimeBucket } from './types';

  let { series }: { series: ToolTimeBucket[] } = $props();
</script>

<GenAiChartCard title="Tool Calls" subtitle="stacked" height="h-40" configFn={() => buildToolStackChart(series)} />
