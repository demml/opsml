
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataProcessor, ModelCard, ModelInterfaceSaveMetadata } from "$lib/components/card/card_interfaces/modelcard";
  import { Info, Diamond, Tags, CheckCheck, Settings } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import ExtraModelMetadata from "./ExtraModelMetadata.svelte";
  import { RegistryType } from "$lib/utils";

let {
    card,
    savedata
  } = $props<{
    card: ModelCard;
    savedata: ModelInterfaceSaveMetadata
  }>();

  let data_processor_keys: string[] = $state([])
  let data_processor_values: DataProcessor[] = $state([])
  let useCardContent = $state('');

  onMount(() => {
    data_processor_keys = Object.keys(savedata.data_processor_map);
    data_processor_values = Object.values(savedata.data_processor_map);

    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('model')
modelcard = registry.load_card(uid="${card.uid}")

# load the model
modelcard.load()
`;
  })

</script>


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-1 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center gap-2">
      <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
        <Info class="w-3.5 h-3.5 text-white" />
      </div>
      <header class="text-primary-950 text-sm font-black uppercase tracking-wide">Model Metadata</header>
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
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-sm"/>
  </div>

  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-primary-100 border-2 border-black rounded-base">
        <Settings class="w-3.5 h-3.5 text-primary-800" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Model Interface</header>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <Pill key="Interface" value={card.metadata.interface_metadata.interface_type} textSize="text-sm"/>
      <Pill key="Task Type" value={card.metadata.interface_metadata.task_type} textSize="text-sm"/>
      <Pill key="Model Type" value={card.metadata.interface_metadata.model_type} textSize="text-sm"/>
      {#if card.metadata.interface_metadata.onnx_session && card.metadata.interface_metadata.onnx_session.schema}
        <Pill key="Onnx Version" value={card.metadata.interface_metadata.onnx_session.schema.onnx_version} textSize="text-sm"/>
      {/if}
    </div>
  </div>

  {#if card.metadata.datacard_uid || card.metadata.experimentcard_uid ||  card.metadata.auditcard_uid}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Diamond class="w-3.5 h-3.5 text-tertiary-950" fill="currentColor" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Linked Cards</header>
      </div>
      <div class="flex flex-wrap gap-1">

        {#if card.metadata.datacard_uid}
          <LinkPill key="Data" uid={card.metadata.datacard_uid} registryType={RegistryType.Data} />
        {/if}

        {#if card.metadata.experimentcard_uid}
          <LinkPill key="Experiment" uid={card.metadata.experimentcard_uid} registryType={RegistryType.Experiment} />
        {/if}
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


  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
        <CheckCheck class="w-3.5 h-3.5 text-black" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Extras</header>
    </div>

    <div class="flex flex-wrap gap-1">
      {#if data_processor_keys && data_processor_keys.length > 0}
        {#each data_processor_values as processor (processor.name)}
          <Pill key="Processor" value={processor.name} textSize="text-sm"/>
        {/each}
      {/if}

      {#if savedata.drift_profile_uri}
        <Pill key="Profile" value="Drift" textSize="text-sm"/>
      {/if}
    </div>

    {#if card.metadata.interface_metadata.model_specific_metadata}
      <div class="flex flex-wrap gap-1">
        <ExtraModelMetadata extra_metadata={card.metadata.interface_metadata.model_specific_metadata}/>
      </div>
    {/if}
  </div>

  
</div>
