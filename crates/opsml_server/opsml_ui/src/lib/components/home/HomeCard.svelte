<script lang="ts">
  import Card from "$lib/components/card/Card.svelte";
  import { type Card as Cards } from "$lib/components/home/types";
  let { 
    header, 
    cards, 

    // header attributes
    headerColor, 
    headerTextColor = "text-black",

    // card attributes
    cardColor, 

  } = $props<{
    header: string;
    cards: Cards[];
    headerTextColor?: string;
    headerColor: string; 
    cardColor: string;


  }>();

  
</script>

<div class="relative flex flex-col items-stretch text-center">
  <div class="inline-block pb-4">
    <div class="{headerColor} inline-block rounded-full border-black border-2 px-2 shadow-small">
      <h2 class="text-xl {headerTextColor} font-bold">
        {header}
      </h2>
    </div>
  </div>


  <div class="flex flex-col items-center gap-4">
    {#each cards as card}
      <Card 
        cardColor={cardColor} 
        {...card.data} 
        />
    {/each}
  </div>
</div>
