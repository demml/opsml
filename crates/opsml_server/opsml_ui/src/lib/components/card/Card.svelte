<script lang="ts">

  import { calculateTimeBetween } from "$lib/utils";
  import {CircuitBoard, Clock, Tag, FlaskConical, Table, BrainCircuit, NotebookText } from 'lucide-svelte';
  import type { Card } from "../home/types";
  import { resolveCardPath } from "./utils";

  let {
    card,
    iconColor,
    badgeColor,
  } = $props<{
    card: Card;
    iconColor: string;
    badgeColor: string;
  }>();


  let cardUrl = $state(resolveCardPath(card));
  let registry = $state(card.type.toLowerCase());

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
      <div><h4 class="truncate font-bold text-smd">{card.data.space}/{card.data.name}</h4></div>
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
          Updated { calculateTimeBetween(card.data.created_at) }
        </time>
      </div>
    </div>
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Tag color={iconColor} />
      </div>
      <div class="text-black">Version: {card.data.version}</div>
    </div>
  </div>
</a>

