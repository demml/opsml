<script lang="ts">
  // version $props() in +page.svelte

  import { goto } from '$app/navigation';
  import type { CardDeck } from '$lib/components/card/card_interfaces/carddeck';
  import type { PageProps } from './$types';
  import DeckMetadata from '$lib/components/card/deck/DeckMetadata.svelte';
  import { Table } from 'lucide-svelte';
  import CardButton from '$lib/components/card/deck/CardButton.svelte';
  let badgeColor = "#40328b";
  let iconColor = "#40328b";

  let { data }: PageProps = $props();
  let deck: CardDeck = data.metadata;

</script>


<div class="flex-1 mx-auto w-11/12 flex justify-center px-4 pb-10">

  <div class="flex flex-wrap pt-4 gap-4 w-full justify-center">

    <div class="bg-primary-200 p-4 flex-1 flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary max-h-[800px] overflow-y-auto self-start min-w-[26rem] max-w-[300px] md:min-w-[26rem] md:max-w-[32rem]">
        <DeckMetadata deck={deck}/>
    </div>

    <div class="flex-1 flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
      <div class="flex flex-row items-center gap-2 py-4">
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <Table color={iconColor} />
        </div>
        <span class="font-bold text-primary-800 text-smd">Card List</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
     

          {#each deck.cards.cards as card}
            <CardButton
              iconColor={iconColor} 
              badgeColor={badgeColor}
              name={card.name}
              space={card.space}
              version={card.version}
              registry={card.registry_type.toLowerCase()}
              alias={card.alias}
            />
          {/each}


   
      </div>
    </div>
  </div>
</div>
  


  