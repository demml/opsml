<script lang="ts">
  import type { PageProps } from './$types';
  import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';
  import type { AgentSpec } from '$lib/components/card/agent/types';
  import AgentPlayground from '$lib/components/card/agent/AgentPlayground.svelte';

  let { data }: PageProps = $props();
  let service: ServiceCard = data.metadata;
  let agentSpec: AgentSpec | undefined = service.service_config.agent;
</script>

{#if !agentSpec}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
    <div class="rounded-lg border-2 border-black shadow-small bg-error-100 p-8 text-center">
      <p class="text-lg font-bold text-error-900">No agent specification found for this service.</p>
    </div>
  </div>
{:else}
  <AgentPlayground
    interfaces={agentSpec.supportedInterfaces}
    agentName={agentSpec.name}
    fullscreen={true}
  />
{/if}
