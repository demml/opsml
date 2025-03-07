<script lang="ts">
  import Card from "$lib/components/card/Card.svelte";
  import { type Card as Cards } from "$lib/components/home/types";
  let { header, cards, headerColor, cardColor } = $props<{
    header: string;
    cards: Cards[];
    headerColor: string; 
    cardColor: string;
  }>();

  
</script>


<div class="relative flex flex-col items-stretch text-center">
  <div class="inline-block mb-2">
    <div class="bg-primary-300 inline-block rounded-full border-black border-2 px-2 shadow-small">
      <h2 class="text-xl text-black font-bold">
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
