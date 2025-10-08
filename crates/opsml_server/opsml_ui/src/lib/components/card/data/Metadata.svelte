
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataCard, DataInterfaceMetadata, DataInterfaceSaveMetadata } from "$lib/components/card/card_interfaces/datacard";
  import { Info, Diamond, Tags } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { Braces, CheckCheck } from 'lucide-svelte';
  import FeatureTable from "../FeatureTable.svelte";
  import { RegistryType } from "$lib/utils";

  let {
      card,
      interfaceMetadata,
      saveMetadata,
    } = $props<{
      card: DataCard;
      interfaceMetadata: DataInterfaceMetadata;
      saveMetadata: DataInterfaceSaveMetadata;
    }>();


    let useCardContent = $state('');
    

    onMount(() => {
      useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('data')
datacard = registry.load_card(uid="${card.uid}")
`;
  })

</script>


<div class="grid grid-cols-1 gap-3 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 font-bold">Metadata</header>
    </div>

    <div>
        <CodeModal 
          code={useCardContent} 
          language="python" 
          message="Paste the following code into your Python script to load the card"
          display="Use this card"
        />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-sm">
    <Pill key="Created At" value={card.created_at} textSize="text-sm"/>
    <Pill key="ID" value={card.uid} textSize="text-sm"/>
    <Pill key="space" value={card.space} textSize="text-sm"/>
    <Pill key="Name" value={card.name} textSize="text-sm"/>
    <Pill key="Version" value={card.version} textSize="text-sm"/>
    <Pill key="Interface Type" value={interfaceMetadata.interface_type} textSize="text-sm"/>
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-sm"/>

  </div>

  {#if card.metadata.experimentcard_uid }
    <div class="flex flex-row items-center pb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-sm font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">
      <LinkPill key="Experiment" uid={card.metadata.experimentcard_uid} registryType={RegistryType.Experiment}/>
    </div>
  {/if}

  {#if card.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center mb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Tags</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each card.tags as tag}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {tag}
        </div>
      {/each}
    </div>
  {/if}

  {#if interfaceMetadata.schema?.items && Object.keys(interfaceMetadata.schema.items).length > 0}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Braces color="#8059b6" />
      <header class="pl-2 text-primary-900 text-sm font-bold">Feature Schema</header>
    </div>

    <div>
      <FeatureTable schema={interfaceMetadata.schema}  />
    </div>

  {/if}


  <div class="flex flex-row items-center mb-1 border-b-2 border-black">
    <CheckCheck color="#8059b6" />
    <header class="pl-2 text-primary-900 text-sm font-bold">Extras</header>
  </div>

  <div class="flex flex-wrap gap-1">
    {#if saveMetadata?.sql_uri}
      <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
        SQL
      </div>
    {/if}
  
    {#if saveMetadata?.data_profile_uri}
      <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
        Data Profile
      </div>
    {/if}
  </div>

 
</div>