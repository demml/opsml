<script lang="ts">
  import type { PageProps } from './$types';
  import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';
  import type { AgentSpec } from '$lib/components/card/agent/types';
  import EnhancedAgentPlayground from '$lib/components/card/agent/EnhancedAgentPlayground.svelte';
  import { AlertCircle } from 'lucide-svelte';
  import type { DeploymentConfig } from '$lib/components/card/card_interfaces/servicecard';

  let { data }: PageProps = $props();
  let service: ServiceCard = data.metadata;
  let agentSpec: AgentSpec | undefined = service.service_config.agent;
  let deploymentConfig: DeploymentConfig[] | undefined = service.deploy;
  
</script>

{#if !agentSpec}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
    <div class="rounded-lg border-2 border-black shadow-small bg-error-100 p-8 text-center">
      <AlertCircle class="w-12 h-12 mx-auto mb-3 text-error-800" />
      <p class="text-lg font-bold text-error-900">No agent specification found for this service.</p>
      <p class="text-sm text-error-800 mt-2">
        This playground requires an A2A-compliant agent configuration.
      </p>
    </div>
  </div>
{:else if agentSpec.skills.length === 0}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
    <div class="rounded-lg border-2 border-black shadow-small bg-warning-100 p-8 text-center">
      <AlertCircle class="w-12 h-12 mx-auto mb-3 text-warning-800" />
      <p class="text-lg font-bold text-warning-900">No skills configured for this agent.</p>
      <p class="text-sm text-warning-800 mt-2">
        Add skills to your agent specification to enable playground interactions.
      </p>
    </div>
  </div>
{:else}
    <EnhancedAgentPlayground
      {agentSpec}
      agentName={agentSpec.name}
      deploymentConfig={deploymentConfig}
    />
{/if}

