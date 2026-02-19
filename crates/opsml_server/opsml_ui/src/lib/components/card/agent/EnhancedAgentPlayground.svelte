<script lang="ts">
  import type { AgentSpec } from "./types";
  import AgentPlaygroundContent from './AgentPlaygroundContent.svelte';
  import type { DeploymentConfig } from "../card_interfaces/servicecard";

  let {
    agentSpec,
    agentName,
    deploymentConfig,
    fullscreen = false
  } = $props<{
    agentSpec: AgentSpec;
    deploymentConfig?: DeploymentConfig[];
    agentName: string;
    fullscreen?: boolean;
  }>();
</script>

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 flex flex-col {fullscreen ? 'h-screen' : 'mx-auto w-11/12 my-6 min-h-[600px]'}">
  <AgentPlaygroundContent {agentSpec} {agentName} {deploymentConfig} showCloseButton={false} />
</div>
