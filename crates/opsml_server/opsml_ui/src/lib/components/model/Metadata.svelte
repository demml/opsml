
<script lang="ts">
  import { onMount } from "svelte";
  import type { DataProcessor, ModelCard, ModelInterfaceSaveMetadata } from "../card/card_interfaces/modelcard";
  import { Info, Diamond, Tags, CheckCheck, Database } from 'lucide-svelte';
  import CodeModal from "../card/CodeModal.svelte";
  import { use } from "marked";

let {
    metadata,
    savedata
  } = $props<{
    metadata: ModelCard;
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
modelcard = registry.load_card(uid="${metadata.uid}")

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
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Created At</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.created_at}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">ID</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.uid}
      </div>
    </div>
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Space</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.repository}
      </div>
    </div>
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Name</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.name}
      </div>
    </div>
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Interface</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.metadata.interface_metadata.interface_type}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Task Type</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.metadata.interface_metadata.task_type}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Model Type</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.metadata.interface_metadata.model_type}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">OpsML Version</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {metadata.metadata.interface_metadata.opsml_version}
      </div>
    </div>

    {#if  metadata.metadata.interface_metadata.onnx_session !== undefined}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
        <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Onnx Version</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {metadata.metadata.interface_metadata.onnx_session.schema.onnx_version}
        </div>
      </div>
    {/if}
  </div>

  {#if metadata.metadata.datacard_uid || metadata.metadata.experimentcard_uid ||  metadata.metadata.auditcard_uid}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">

      {#if metadata.metadata.datacard_uid}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
          <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Data</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            <a href="/opsml/data/card/home?uid={metadata.metadata.datacard_uid}" class="text-primary-900">
              Link
            </a>
          </div>
        </div>
      {/if}

      {#if metadata.metadata.experimentcard_uid}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
          <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Experiment</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            <a href="/opsml/experiment/card/home?uid={metadata.metadata.experimentcard_uid}" class="text-primary-900">
              Link
            </a>
          </div>
        </div>
      {/if}
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


  <div class="flex flex-row items-center mb-1 border-b-2 border-black">
    <CheckCheck color="#8059b6" />
    <header class="pl-2 text-primary-900 text-lg font-bold">Extras</header>
  </div>

  <div class="flex flex-wrap gap-1">
    {#if data_processor_keys && data_processor_keys.length > 0}
      {#each data_processor_values as processor}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
          <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Processor</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            {processor.name}
          </div>
        </div>
      {/each}
    {/if}

    {#if savedata.drift_profile_uri}
      <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
        Drift Profile
      </div>
    {/if}

  </div>
  
</div>