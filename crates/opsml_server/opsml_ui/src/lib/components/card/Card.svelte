<script lang="ts">

  import { calculateTimeBetween } from "$lib/utils";
  import { goto } from "$app/navigation";
  import {CircuitBoard, Clock, Tag, FlaskConical, Table, BrainCircuit, NotebookText } from 'lucide-svelte';

  let {
    name,
    space,
    version,
    created_at,
    registry,
    iconColor,
    badgeColor,
  } = $props<{
    name: string;
    space: string;
    version: string;
    created_at: string;
    registry: string;
    iconColor: string;
    badgeColor: string;
  }>();

  // function to navigate to the card page
  function navigateToCardPage() {
    // navigate to the card page
    let registry_name = registry.toLowerCase();
    goto(`/opsml/${registry_name}/card/home?space=${space}&name=${name}&version=${version}`);
  }


</script>

<button class="text-black rounded-base shadow border-2 border-black bg-surface-300 w-full max-w-[30em] h-[5em] overflow-auto whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToCardPage}>
  <div class="flex items-center justify-between">
    <div class="flex items-center justify-start gap-2 mb-1">
      <div class="ml-2">
        <CircuitBoard color={iconColor} />
      </div>
      <div><h4 class="truncate font-bold text-smd">{space}/{name}</h4></div>
    </div>
    <div class="mr-2">

      {#if registry === "model"}
        <BrainCircuit color={badgeColor} />
      {:else if registry === "data"}
        <Table color={badgeColor} />
      {:else if registry === "prompt"}
        <NotebookText color={badgeColor} />
      {:else if registry === "experiment"}
        <FlaskConical color={badgeColor} />
      {/if}
  
    </div>
  </div>
  <div class="flex items-center justify-start gap-2 whitespace-nowrap text-xs">
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Clock color={iconColor} />
      </div>
      <div>
        <time datetime={ Date() } >
          Updated { calculateTimeBetween(created_at) }
        </time>
      </div>
    </div>
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Tag color={iconColor} />
      </div>
      <div class="text-black">Version: {version}</div>
    </div>
  </div>
</button>

