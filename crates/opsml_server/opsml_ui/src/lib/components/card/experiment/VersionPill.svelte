<script lang="ts">
  import type { BaseCard } from "$lib/components/home/types";

 
    let { 
       card,
       active,
       setActive
     } = $props<{
        card: BaseCard;
        active: boolean;
        setActive: (card: BaseCard) => void;
     }>();
  
  </script>
  
{#if active}
  <button class="inline-flex items-stretch overflow-hidden rounded-lg border-2 border-primary-700 w-fit" onclick={() => setActive(card)}>
    <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic flex items-center justify-center">{card.version}</div> 
      <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950 flex items-center justify-center">
        {card.created_at}
  </button>
{:else}
<button class="inline-flex items-stretch overflow-hidden rounded-lg bg-parimary-500 shadow shadow-hover border-2 border-black w-fit" onclick={() => setActive(card)}>
  <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic flex items-center justify-center">{card.version}</div> 
    <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950 flex items-center justify-center">
      {card.created_at}
    </div>
  </button>
{/if}
