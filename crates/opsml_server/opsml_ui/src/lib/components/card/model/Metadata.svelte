
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataProcessor, ModelCard, ModelInterfaceSaveMetadata } from "$lib/components/card/card_interfaces/modelcard";
  import { Info, Diamond, Tags, CheckCheck} from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import ExtraModelMetadata from "./ExtraModelMetadata.svelte";

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

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-2xl font-bold">Metadata</header>
    </div>

    <div>
        <!--<button type="button" class="btn btn-md bg-primary-500 text-black justify-end mb-2 text-base shadow shadow-hover border-black border-2" >Use this card</button>-->
        <CodeModal code={useCardContent} language="python" />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-base">
    
    <Pill key="Created At" value={card.created_at} textSize="text-base"/>
    <Pill key="ID" value={card.uid} textSize="text-base"/>
    <Pill key="Space" value={card.space} textSize="text-base"/>
    <Pill key="Name" value={card.name} textSize="text-base"/>
    <Pill key="Interface" value={card.metadata.interface_metadata.interface_type} textSize="text-base"/>
    <Pill key="Task Type" value={card.metadata.interface_metadata.task_type} textSize="text-base"/>
    <Pill key="Model Type" value={card.metadata.interface_metadata.model_type} textSize="text-base"/>
    <Pill key="Version" value={card.opsml_version} textSize="text-base"/>


    {#if  card.metadata.interface_metadata.onnx_session !== undefined}
      <Pill key="Onnx Version" value={card.metadata.interface_metadata.onnx_session.schema.onnx_version} textSize="text-base"/>
    {/if}
  </div>

  {#if card.metadata.datacard_uid || card.metadata.experimentcard_uid ||  card.metadata.auditcard_uid}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">

      {#if card.metadata.datacard_uid}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
          <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Data</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            <a href="/opsml/data/card/home?uid={card.metadata.datacard_uid}" class="text-primary-900">
              Link
            </a>
          </div>
        </div>
      {/if}

      {#if card.metadata.experimentcard_uid}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
          <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Experiment</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            <a href="/opsml/experiment/card/home?uid={card.metadata.experimentcard_uid}" class="text-primary-900">
              Link
            </a>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  {#if card.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center mb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-lg font-bold">Tags</header>
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


  <div class="flex flex-row items-center mb-1 border-b-2 border-black">
    <CheckCheck color="#8059b6" />
    <header class="pl-2 text-primary-900 text-lg font-bold">Extras</header>
  </div>

  <div class="flex flex-wrap gap-1">
    {#if data_processor_keys && data_processor_keys.length > 0}
      {#each data_processor_values as processor}
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