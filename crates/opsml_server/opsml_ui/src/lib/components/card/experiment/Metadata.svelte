
<script lang="ts">
  import { onMount } from "svelte";
  import type { ExperimentCard, ComputeEnvironment} from "$lib/components/card/card_interfaces/experimentcard";
  import { Info, Diamond, Tags, CheckCheck, Database } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";


let {
    metadata,
  } = $props<{
    metadata: ExperimentCard;
  }>();


  let useCardContent = $state('');

  onMount(() => {
    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('experiment')
experimentcard = registry.load_card(uid="${metadata.uid}")
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
    <Pill key="Created By" value={metadata.created_by} />
    <Pill key="ID" value={metadata.uid} />
    <Pill key="Repository" value={metadata.repository} />
    <Pill key="Name" value={metadata.name} />
    <Pill key="Version" value={metadata.version} />
    <Pill key="OpsML Version" value={metadata.metadata.interface_metadata.opsml_version} />

    {#if  metadata.metadata.interface_metadata.onnx_session !== undefined}
      <Pill key="Onnx Version" value={metadata.metadata.interface_metadata.onnx_session.schema.onnx_version} />
    {/if}
  </div>

  {#if metadata.uids.datacard_uids || metadata.uids.modelcard_uids ||  metadata.uids.promptcard_uids ||  metadata.uids.experimentcard_uids}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">

      {#if metadata.uids.datacard_uids}
        {#each metadata.uids.datacard_uids as datacard_uid}
          <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
            <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Data</div> 
            <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
              <a href="/opsml/data/card/home?uid={datacard_uid}" class="text-primary-900">
                Link
              </a>
            </div>
          </div>
        {/each}
      {/if}

      {#if metadata.uids.experimentcard_uids}
        {#each metadata.uids.experimentcard_uids as experimentcard_uid}
          <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
            <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Experiment</div> 
            <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
              <a href="/opsml/experiment/card/home?uid={experimentcard_uid}" class="text-primary-900">
                Link
              </a>
            </div>
          </div>
        {/each}
      {/if}

      {#if metadata.uids.modelcard_uids}
        {#each metadata.uids.modelcard_uids as modelcard_uid}
          <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
            <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Model</div> 
            <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
              <a href="/opsml/model/card/home?uid={modelcard_uid}" class="text-primary-900">
                Link
              </a>
            </div>
          </div>
        {/each}
      {/if}

      {#if metadata.uids.promptcard_uids}
        {#each metadata.uids.promptcard_uids as promptcard_uid}
          <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7">
            <div class="border-r border-primary-700 px-2 text-primary-950 bg-primary-100 italic">Prompt</div> 
            <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
              <a href="/opsml/prompt/card/home?uid={promptcard_uid}" class="text-primary-900">
                Link
              </a>
            </div>
          </div>
        {/each}
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
    <header class="pl-2 text-primary-900 text-lg font-bold">Compute Env</header>
  </div>

  <div class="flex flex-col space-y-1 text-base">
    <Pill key="CPU Count" value={metadata.compute_environment.cpu_count} />
    <Pill key="Total Memory" value={metadata.compute_environment.total_memory} />
    <Pill key="Total Swap" value={metadata.compute_environment.total_swap} />
    <Pill key="System" value={metadata.compute_environment.system} />
    <Pill key="OS Version" value={metadata.compute_environment.os_version} />
    <Pill key="Hostname" value={metadata.compute_environment.hostname} />
    <Pill key="Python" value={metadata.compute_environment.python_version} />
  </div>

  
</div>