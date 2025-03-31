
<script lang="ts">
  import type { BaseCard } from "$lib/components/home/types";
  import { onMount } from "svelte";
  import { getCardMetrics } from "./util";
  import type { PlotType } from "./types";

    let { 
      currentCard,
      selectedMetrics,
      selectedCards,
      plotType,
    } = $props<{
      currentCard: BaseCard;
      selectedMetrics: string[];
      selectedCards: BaseCard[];
      plotType: PlotType;
    }>();
  
    // state
    let resetZoom: boolean = $state(false);
  
    let resetZoomClicked = () => {
      resetZoom = !resetZoom;
    }

    onMount(async () => {
      // Set the initial value of resetZoom to false
      resetZoom = false;
      let metrics = await getCardMetrics(currentCard.uid, selectedMetrics);
    });

  </script>


<div class="bg-white p-4 border-2 border-black rounded-lg shadow h-[500px]">
</div>
  