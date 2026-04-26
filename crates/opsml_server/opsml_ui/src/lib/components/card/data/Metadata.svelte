
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataCard, DataInterfaceMetadata, DataInterfaceSaveMetadata } from "$lib/components/card/card_interfaces/datacard";
  import { Info, Diamond, Tags, Braces, CheckCheck } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
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


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-1 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center gap-2">
      <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
        <Info class="w-3.5 h-3.5 text-white" />
      </div>
      <header class="text-primary-950 text-sm font-black uppercase tracking-wide">Data Metadata</header>
    </div>

    <CodeModal 
      code={useCardContent} 
      language="python" 
      message="Paste the following code into your Python script to load the card"
      display="Use this card"
    />
  </div>


  <div class="flex flex-col gap-1.5 text-sm">
    <Pill key="Created At" value={card.created_at} textSize="text-sm"/>
    <Pill key="ID" value={card.uid} textSize="text-sm"/>
    <Pill key="Space" value={card.space} textSize="text-sm"/>
    <Pill key="Name" value={card.name} textSize="text-sm"/>
    <Pill key="Version" value={card.version} textSize="text-sm"/>
    <Pill key="Interface Type" value={interfaceMetadata.interface_type} textSize="text-sm"/>
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-sm"/>

  </div>

  {#if card.metadata.experimentcard_uid }
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Diamond class="w-3.5 h-3.5 text-tertiary-950" fill="currentColor" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Linked Cards</header>
      </div>

      <div class="flex flex-wrap gap-1">
        <LinkPill key="Experiment" uid={card.metadata.experimentcard_uid} registryType={RegistryType.Experiment}/>
      </div>
    </div>
  {/if}

  {#if card.tags.length > 0}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Tags class="w-3.5 h-3.5 text-tertiary-950" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Tags</header>
      </div>

      <div class="flex flex-wrap gap-1">
        {#each card.tags as tag (tag)}
          <span class="badge bg-primary-100 text-primary-900 border border-black shadow-small text-xs font-bold">
            {tag}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  {#if interfaceMetadata.schema?.items && Object.keys(interfaceMetadata.schema.items).length > 0}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
          <Braces class="w-3.5 h-3.5 text-black" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Feature Schema</header>
      </div>

      <div>
        <FeatureTable schema={interfaceMetadata.schema}  />
      </div>
    </div>

  {/if}


  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
        <CheckCheck class="w-3.5 h-3.5 text-black" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Extras</header>
    </div>

    <div class="flex flex-wrap gap-1">
      {#if saveMetadata?.sql_uri}
        <span class="badge bg-primary-100 text-primary-900 border border-black shadow-small text-xs font-bold">
          SQL
        </span>
      {/if}
    
      {#if saveMetadata?.data_profile_uri}
        <span class="badge bg-primary-100 text-primary-900 border border-black shadow-small text-xs font-bold">
          Data Profile
        </span>
      {/if}
    </div>
  </div>

 
</div>
