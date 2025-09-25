<script lang="ts">
  import type { ServiceCard, DeploymentConfig, ServiceConfig, ServiceMetadata } from "$lib/components/card/card_interfaces/servicecard";

  let {config} = $props<{config: DeploymentConfig}>();
  import { Rocket } from 'lucide-svelte';
  import Pill from "$lib/components/utils/Pill.svelte";

</script>

<div class="flex flex-row items-center pb-1 border-b-2 border-black">
  <Rocket color="#8059b6" />
  <header class="pl-2 text-primary-900 text-sm font-bold">Deployment Configuration</header>

  <div class="flex flex-col space-y-1 text-sm">
    <Pill key="Environment" value={config.environment} textSize="text-sm" />
    {#if config.provider}
      <Pill key="Provider" value={config.provider} textSize="text-sm" />
    {/if}
    {#if config.location}
      {#each config.location as loc}
        <Pill key="Location" value={loc} textSize="text-sm" />
      {/each}
    {/if}
  </div>

</div>