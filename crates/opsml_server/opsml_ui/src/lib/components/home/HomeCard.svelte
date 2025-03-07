<script lang="ts">
  import { onMount } from "svelte";
  import Card from "$lib/components/card/Card.svelte";
  import { type Card as Cards } from "$lib/components/home/types";
  let { header, cards } = $props<{
    header: string;
    cards: Cards[]; // You can make this more specific based on your needs
  }>();

  // add onMount and console.log(cards) to see what is being passed to the component
  //onMount(() => {
  //   console.log(cards);
  // });

  
</script>


<div class="relative flex flex-col items-stretch text-center">
  <h2 class="mb-3 flex items-center justify-center text-xl 2xl:mb-4 2xl:text-xl text-primary-800">
    {header}
  </h2>
  <div class="flex flex-col items-center gap-4">
    {#each cards as card}
      <Card {...card.data} />
    {/each}
  </div>
</div>