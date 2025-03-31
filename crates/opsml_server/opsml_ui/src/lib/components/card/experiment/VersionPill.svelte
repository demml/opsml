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
  <label class="flex items-center space-x-2">
    <input class="checkbox bg-primary-500 h-5 w-5 border-1 border-black rounded-none" type="checkbox" checked onchange={() => setActive(card)}/>
    <p class="text-black">{card.version}</p>
  </label>
{:else}
<label class="flex items-center space-x-2">
  <input class="checkbox h-5 w-5 bg-white h-5 w-5 border-1 border-black rounded-none" type="checkbox" onchange={() => setActive(card)}/>
  <p class="text-black">{card.version}</p>
</label>
{/if}
