
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataCard, DataInterfaceMetadata, DataInterfaceSaveMetadata } from "$lib/components/card/card_interfaces/datacard";
  import { Info, Diamond, Tags } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import { Braces, CheckCheck } from 'lucide-svelte';
  import FeaturePill from "./FeaturePill.svelte";
  import { type Feature } from "$lib/components/card/card_interfaces/datacard";

  let {
      metadata,
    } = $props<{
      metadata: DataCard;
    }>();


    let useCardContent = $state('');
    let interfaceData: DataInterfaceMetadata = $state(metadata.metadata.interface_metadata);
    let saveMetadata: DataInterfaceSaveMetadata = $state(metadata.metadata.interface_metadata.save_metadata);
    

    onMount(() => {
      useCardContent = `from opsml import CardRegistry

  # load the card
  registry = CardRegistry('data')
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
    <Pill key="Repository" value={metadata.repository} />
    <Pill key="Name" value={metadata.name} />
    <Pill key="Version" value={metadata.version} />
    <Pill key="Interface Type" value={interfaceData.interface_type} />
    <Pill key="OpsML Version" value={metadata.opsml_version} />

  </div>

  {#if metadata.metadata.experimentcard_uid }
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
        <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Experiment</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          <a href="/opsml/experiment/card/home?uid={metadata.metadata.experimentcard_uid}" class="text-primary-900">
            Link
          </a>
        </div>
      </div>
    </div>
  {/if}

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

  {#if metadata.metadata.schema?.items && Object.keys(metadata.metadata.schema.items).length > 0}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Braces color="#8059b6" />
      <header class="pl-2 text-primary-900 text-lg font-bold">Feature Schema</header>
    </div>

    <div class="flex flex-col space-y-1 text-base text-black">(name, type, shape)</div>

    <div class="flex flex-col space-y-1 text-base">
      {#each Object.entries(metadata.metadata.schema.items) as [name, feature]}
        <FeaturePill 
          key={name} 
          type={(feature as Feature).feature_type} 
          shape={(feature as Feature).shape} 
        />
      {/each}
    </div>
  {/if}


  <div class="flex flex-row items-center mb-1 border-b-2 border-black">
    <CheckCheck color="#8059b6" />
    <header class="pl-2 text-primary-900 text-lg font-bold">Extras</header>
  </div>

  <div class="flex flex-wrap gap-1">
    {#if saveMetadata.sql_uri}
      <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
        SQL
      </div>
    {/if}

    {#if saveMetadata.data_profile_uri}
      <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
        Data Profile
      </div>
    {/if}
  </div>

  {#if interfaceData.data_splits.splits.length > 0}
    <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
      Data Splits
    </div>
  {/if}

</div>