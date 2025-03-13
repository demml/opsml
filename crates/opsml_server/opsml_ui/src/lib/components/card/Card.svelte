<script lang="ts">

  import { calculateTimeBetween } from "$lib/utils";
  import { goto } from "$app/navigation";
  import {CircuitBoard, Clock, Tag, FlaskConical, Table, BrainCircuit, NotebookText } from 'lucide-svelte';

  let {
    name,
    repository,
    version,
    created_at,
    registry,
    uid,
    iconColor,
  } = $props<{
    name: string;
    repository: string;
    version: string;
    created_at: string;
    registry: string;
    uid: string;
    cardColor: string;
  }>();

  // function to navigate to the card page
  function navigateToCardPage() {
    // navigate to the card page
    goto(`/opsml/${registry}/card/home?uid=${uid}`);
  }


</script>

<button class="text-black rounded-base shadow border-2 border-black bg-surface-300 w-[400px] h-[75px] overflow-hidden whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToCardPage}>
  <div class="flex items-center justify-between">
    <div class="flex items-center justify-start gap-2 mb-1">
      <div class="ml-2">
        <CircuitBoard color={iconColor} />
      </div>
      <div><h4 class="truncate font-bold text-lg">{repository}/{name}</h4></div>
    </div>
    <div class="mr-2">

      {#if registry === "model"}
        <BrainCircuit color="#8059b6" />
      {:else if registry === "data"}
        <Table color="#5fd68d" />
      {:else if registry === "prompt"}
        <NotebookText color="#f9b25e" />
      {:else if registry === "experiment"}
        <FlaskConical color="#f54c54" />
      {/if}
  
    </div>
  </div>
  <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs">
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

