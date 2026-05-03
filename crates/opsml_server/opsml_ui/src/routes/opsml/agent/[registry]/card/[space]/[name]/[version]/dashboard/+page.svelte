<script lang="ts">
  import AgentGenAiDashboard from '$lib/components/card/agent/observability/AgentGenAiDashboard.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<AgentGenAiDashboard bundle={data.bundle} />
