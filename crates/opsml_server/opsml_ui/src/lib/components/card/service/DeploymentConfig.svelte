<script lang="ts">
  import type { DeploymentConfig,  Resources } from "$lib/components/card/card_interfaces/servicecard";

  let {config} = $props<{config: DeploymentConfig}>();
  import { Rocket, Earth, EthernetPort, Link, Cpu } from 'lucide-svelte';
  import Pill from "$lib/components/utils/Pill.svelte";
  import ExternalLinkPill from "$lib/components/utils/ExternalLinkPill.svelte";
  let resources: Resources | undefined = $state(config.resources);
  let links: Record<string, string> | undefined = $state(config.links);

</script>
<div class="grid grid-cols-1 gap-3 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    <div class="flex flex-row items-center pt-2">
      <Rocket color="#e55455"/>
      <header class="pl-2 text-primary-950 text-base font-bold">Deployment Configuration</header>
    </div>
  </div>

  <div class="flex flex-col space-y-1 text-sm">
    <Pill key="Environment" value={config.environment} textSize="text-sm" />
    {#if config.provider}
      <Pill key="Provider" value={config.provider} textSize="text-sm" />
    {/if}
  </div>

  {#if config.location}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Earth color="#60d68d" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Location</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each config.location as loc}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {loc}
        </div>
      {/each}
    </div>
  {/if}

  {#if config.endpoints.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <EthernetPort color="#8059b6" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Endpoints</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each config.endpoints as endpoint}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {endpoint}
        </div>
      {/each}
    </div>
  {/if}

  {#if resources }
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Cpu color="#40c1ff" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Resources</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      <div class="flex flex-col space-y-1 gap-1 border-2 border-primary-800 rounded-lg p-2">
        <div class="flex flex-row items-center">
            <header class="pl-2 text-primary-900 text-sm font-bold">CPU</header>
        </div>
        <div class="flex flex-col space-y-1 text-sm">
          <Pill key="CPU" value={resources.cpu.toString()} textSize="text-sm" />
          <Pill key="Memory" value={resources.memory} textSize="text-sm" />
          <Pill key="Storage" value={resources.storage} textSize="text-sm" />
        </div>
      </div>

      {#if resources.gpu}
        <div class="flex flex-col space-y-1 gap-1 border-2 border-primary-800 rounded-lg p-2">
          <div class="flex flex-row items-center">
              <header class="pl-2 text-primary-900 text-sm font-bold">GPU</header>
          </div>
          <div class="flex flex-col space-y-1 text-sm">
            <Pill key="Type" value={resources.gpu.type} textSize="text-sm" />
            <Pill key="Count" value={resources.gpu.count.toString()} textSize="text-sm" />
            <Pill key="Memory" value={resources.gpu.memory} textSize="text-sm" />
          </div>
        </div>
      {/if}
    </div>
  {/if}

  {#if links && Object.keys(links).length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Link color="#fddc5a" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Links</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1 text-sm">
      {#each Object.entries(links) as [key, value]}
        <ExternalLinkPill key={key} link={value} />
      {/each}
    </div>
  {/if}


</div>
