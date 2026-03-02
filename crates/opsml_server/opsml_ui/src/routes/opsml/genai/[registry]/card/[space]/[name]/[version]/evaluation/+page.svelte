<script lang="ts">
  import type { PageProps } from './$types';
  import { RegistryType } from '$lib/utils';
  import AgentEvalDashboard from '$lib/components/card/agent/evaluation/AgentEvalDashboard.svelte';
  import PromptEvalDashboard from '$lib/components/card/prompt/PromptEvalDashboard.svelte';

  let { data }: PageProps = $props();
  let isAgent = $derived(data.registryType === RegistryType.Agent);
</script>

{#if isAgent}
  <AgentEvalDashboard
    agentName={data.metadata.name}
    agentVersion={data.metadata.version}
    agentPromptEvals={data.agentPromptEvals ?? []}
  />
{:else if data.monitoringData}
  <PromptEvalDashboard
    initialMonitoringData={data.monitoringData}
    metadata={data.metadata}
    registryType={data.registryType}
  />
{/if}
