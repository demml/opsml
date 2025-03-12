
<script lang="ts">
  import type { ModelCard } from "../card/card_interfaces/modelcard";
  import { Info } from 'lucide-svelte';

let {
    metadata
  } = $props<{
    metadata: ModelCard;
  }>();

</script>


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-2xl font-bold">Metadata</header>
    </div>

    <div>
        <button type="button" class="btn btn-md bg-primary-500 text-black justify-end mb-2 text-base shadow shadow-hover border-black border-2" >Use this card</button>
    </div>

  </div>

  <div class="flex flex-col space-y-1 tex-base">
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
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Onnx Version</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {metadata.metadata.interface_metadata.onnx_session.schema.onnx_version}
        </div>
      </div>
    {/if}

  </div>

</div>