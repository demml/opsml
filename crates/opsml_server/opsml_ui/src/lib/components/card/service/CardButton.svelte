<script lang="ts">

  import { goto } from "$app/navigation";
  import { RegistryType } from "$lib/utils";
  import {CircuitBoard, KeyIcon, Tag, FlaskConical, Table, BrainCircuit, NotebookText } from 'lucide-svelte';
  import { resolveCardPathFromArgs } from "../utils";

  let {
    name,
    space,
    version,
    alias,
    registry,
    iconColor,
    badgeColor,
  } = $props<{
    name: string;
    space: string;
    version: string;
    alias: string;
    registry: RegistryType;
    iconColor: string;
    badgeColor: string;
  }>();

  

  let cardUrl = $state(resolveCardPathFromArgs(registry, space, name, version));


</script>

<a 
  class="p-2 text-black rounded-base shadow border-2 border-black bg-surface-300 w-full max-w-[30em] h-[5em] overflow-auto whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" 
  href={cardUrl}
  data-sveltekit-preload-data="hover"
  >
  <div class="flex items-center justify-between">
    <div class="flex items-center justify-start gap-2 mb-1">
      <div class="ml-2">
        <CircuitBoard color={iconColor} />
      </div>
      <div><h4 class="truncate font-bold text-smd">{space}/{name}</h4></div>
    </div>
    <div class="mr-2">

      {#if registry === RegistryType.Model}
        <BrainCircuit color={badgeColor} />
      {:else if registry === RegistryType.Data}
        <Table color={badgeColor} />
      {:else if registry === RegistryType.Prompt}
        <NotebookText color={badgeColor} />
      {:else if registry === RegistryType.Experiment}
        <FlaskConical color={badgeColor} />
      {/if}
  
    </div>
  </div>
  <div class="flex items-center justify-start gap-2 whitespace-nowrap text-xs">
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <KeyIcon color={iconColor} />
      </div>
      <div>
        <div class="text-black">Alias: {alias}</div>
      </div>
    </div>
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Tag color={iconColor} />
      </div>
      <div class="text-black">Version: {version}</div>
    </div>
  </div>
</a>

