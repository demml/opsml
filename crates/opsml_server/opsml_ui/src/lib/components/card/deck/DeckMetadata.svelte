
<script lang="ts">
  import { onMount } from "svelte";
  import type { CardDeck } from "$lib/components/card/card_interfaces/carddeck";
  import { Info, Diamond } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { RegistryType } from "$lib/utils";
  import { python } from "svelte-highlight/languages";

let {
    deck,
  } = $props<{
    deck: CardDeck;
  }>();


  let useCardContent = $state('');


  onMount(() => {
 
    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('deck')
deck = registry.load_card(uid="${deck.uid}")

# load the model
deck.load()
`;
  })

</script>


<div class="grid grid-cols-1 gap-3 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-base font-bold">Metadata</header>
    </div>

    <div>
        <CodeModal 
          code={useCardContent} 
          language={python} 
          message="Paste the following code into your Python script to load the card"
          display="Use this card"
        />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-sm">

    <Pill key="Created At" value={deck.created_at} textSize="text-sm"/>
    <Pill key="ID" value={deck.uid} textSize="text-sm"/>
    <Pill key="Space" value={deck.space} textSize="text-sm"/>
    <Pill key="Name" value={deck.name} textSize="text-sm"/>
    <Pill key="Version" value={deck.opsml_version} textSize="text-sm"/>

  </div>

  {#if deck.experimentcard_uid }
    <div class="flex flex-row items-center pb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-sm font-bold">Extra</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">
      {#if deck.experimentcard_uid}
        <LinkPill key="Experiment" value={deck.experimentcard_uid} registryType={RegistryType.Experiment} />
      {/if}
    </div>
  {/if}
</div>