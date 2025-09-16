<script lang="ts">
  import Card from "$lib/components/card/Card.svelte";
  import { type Card as Cards } from "$lib/components/home/types";
  import type { RegistryType } from "$lib/utils";
  let { 
    header, 
    cards, 
    // header attributes
    headerColor, 
    headerTextColor = "text-black",
    iconColor,
    badgeColor

  } = $props<{
    header: string;
    cards: Cards[];
    headerTextColor?: string;
    headerColor: string; 
    iconColor: string;
    badgeColor: string;

  }>();

  
</script>

<div class="flex flex-col w-full">
  <!-- Header -->
  <div class="flex justify-center mb-4">
    <div class="{headerColor} rounded-full border-black border-2 px-2 shadow-small">
      <h2 class="{headerTextColor} font-bold">{header}</h2>
    </div>
  </div>

  <!-- Cards -->
  <div class="flex flex-col gap-4">
    {#each cards as card}
      <div class="flex justify-center w-full">
        <Card 
          iconColor={iconColor} 
          badgeColor={badgeColor}
          card={card}
        />
      </div>
    {/each}
  </div>
</div>
