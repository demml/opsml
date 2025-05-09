
<script lang="ts">
  import { onMount } from "svelte";
  import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
  import { Info, Diamond, Tags } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import { Braces, CheckCheck } from 'lucide-svelte';


  let {
      metadata,
    } = $props<{
      metadata: PromptCard;
    }>();


    let useCardContent = $state('');
    

    onMount(() => {
      useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('prompt')
datacard = registry.load_card(uid="${metadata.uid}")
`;
  })

</script>


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-2xl font-bold">Metadata</header>
    </div>

    <div>
        <CodeModal code={useCardContent} language="python" />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-base">
    <Pill key="Created At" value={metadata.created_at} />
    <Pill key="ID" value={metadata.uid} />
    <Pill key="space" value={metadata.space} />
    <Pill key="Name" value={metadata.name} />
    <Pill key="Version" value={metadata.version} />
    <Pill key="OpsML Version" value={metadata.opsml_version} />

  </div>

 

  {#if metadata.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center mb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-lg font-bold">Tags</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each metadata.tags as tag}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {tag}
        </div>
      {/each}
    </div>
  {/if}

  



</div>