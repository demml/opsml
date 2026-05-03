<script lang="ts">
  import GenAiChartCard from './GenAiChartCard.svelte';
  import { buildCostChart } from './charts';
  import type { ModelCostBreakdown } from './types';

  let { costByModel }: { costByModel: ModelCostBreakdown[] } = $props();

  const cfg = $derived(() => buildCostChart(costByModel));
</script>

<GenAiChartCard
  title="Cost by Model"
  subtitle="$ total"
  height="h-40"
  configFn={cfg}
/>
