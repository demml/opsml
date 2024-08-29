<script lang="ts">

  import { type RunCard , type Card } from "$lib/scripts/types";
  import { loadModal } from "$lib";
  import Fa from 'svelte-fa'
  import { faTag, faFileContract, faCircleInfo, faComputer} from '@fortawesome/free-solid-svg-icons'

  
  import { type ModalStore} from '@skeletonlabs/skeleton';
  import CodeModal from '$lib/components/CodeModal.svelte';
  import type { ModalComponent, ModalSettings } from '@skeletonlabs/skeleton';
  import { python } from "svelte-highlight/languages";
  import MetadataPill from "$lib/components/MetadataPill.svelte";
  import MetadataPillList from "$lib/components/MetadataPillList.svelte";
  
  export let metadata: RunCard;
  export let card: Card;
  let registry: string = "run";

  let memory: string = `${(metadata.compute_environment.memory / (1024**3)).toFixed(1)} GB`;
  let disk_space: string = `${(metadata.compute_environment.disk_space / (1024**3)).toFixed(2)} GB`;
  
  function getGpuMemory(memory: Map<string, number>): string {
    let gpu_memory: number = 0;
    const keys = Object.keys(memory);

    keys.forEach((key) => {
      gpu_memory += memory[key];
    });
  
    return `${(gpu_memory / (1024**3)).toFixed(2)} GB`;
  }
  
  const modalStore: ModalStore = loadModal();
  
  async function showModal() {
  
    const modalComponent: ModalComponent = {
      ref: CodeModal,
      props: { 
        uid: card.uid,
        registry: registry,
        modalStore: modalStore
      },
    };
  
    const modal: ModalSettings = {
    type: 'component',
    component: modalComponent,
    };
  
    modalStore.trigger(modal);
  }
  
  
</script>

<div class="rounded-lg border-2 border-darkpurple p-4 shadow-md shadow-primary-500 mb-2 overflow-x-scroll bg-white">
  <div class="flex flex-row justify-between mb-2 items-center border-b-2 border-gray-400">
  
    <div class="flex flex-row items-center pt-2">
      <Fa icon={faCircleInfo} color="#04cd9b"/>
      <header class="pl-2 text-darkpurple text-lg font-bold">Metadata</header>
    </div>
    <div>
      <button type="button" class="btn btn-sm bg-darkpurple text-white justify-end mb-2" on:click={() => showModal()}>Use this card</button>
    </div>

  </div>
  
  <div class="flex flex-col space-y-1">

    <MetadataPill title="ID" value={card.uid} colspan={undefined}/>
    <MetadataPill title="Name" value={metadata.name} colspan={undefined}/>
    <MetadataPill title="Repository" value={metadata.repository} colspan={undefined}/>
    <MetadataPill title="Version" value={metadata.version} colspan={undefined}/>

  </div>

  <div class="flex flex-row items-center mb-2 pt-2 border-b-2 border-gray-400">
    <Fa icon={faComputer} color="#04cd9b"/>
    <header class="pl-2 text-darkpurple text-lg font-bold">Compute</header>
  </div>

  <div class="px-2 pb-2 mb-2 shadow-md rounded-md">
  
      <header class="pl-1 text-darkpurple text-md font-semibold">System</header>
      <div class="pl-2 flex-nowrap items-center space-1">

        <MetadataPill title="CPU count" value={metadata.compute_environment.cpu_count} colspan={undefined}/>
        <MetadataPill title="Memory" value={memory} colspan={undefined}/>
        <MetadataPill title="Disk Space" value={disk_space} colspan={undefined}/>

      </div>
  </div>

  <div class="px-2 pb-2 mb-2 shadow-md rounded-md rounded-md">
    
    <header class="pl-1 text-darkpurple text-md font-semibold">Architecture</header>
    <div class="pl-2 flex-nowrap items-center space-1">

      <MetadataPill title="System" value={metadata.compute_environment.system} colspan={undefined}/>
      <MetadataPill title="Release" value={metadata.compute_environment.release} colspan={undefined}/>

      <MetadataPill 
        title="Bits" 
        value={metadata.compute_environment.architecture_bits} 
        colspan={undefined}/>
    </div>
  </div>

  <div class="px-2 pb-2 mb-2 shadow-md rounded-md rounded-md">
    
    <header class="pl-1 text-darkpurple text-md font-semibold">Python</header>
    <div class="pl-2 flex-nowrap items-center space-1">

      <MetadataPill 
      title="Python" 
      value={metadata.compute_environment.python_version}
      colspan={undefined}/>

      <MetadataPill 
      title="Compiler" 
      value={metadata.compute_environment.python_compiler}
      colspan={undefined}/>

    </div>
  </div>

  {#if metadata.compute_environment.gpu_count > 0}
    <div class="px-2 pb-2 mb-2 shadow-md rounded-md rounded-md">
      
      <header class="pl-2 text-darkpurple text-md font-semibold">GPU</header>
      <div class="flex-nowrap items-center gap-2">

        <MetadataPill 
        title="GPU count" 
        value={metadata.compute_environment.gpu_count}
        colspan={undefined}/>

        <MetadataPill 
        title="GPU memory" 
        value={getGpuMemory(metadata.compute_environment.gpu_device_memory)}
        colspan={undefined}/>

        <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
          <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">Devices</div> 
          {#each metadata.compute_environment.gpu_devices as device, index}
            {#if index !== metadata.compute_environment.gpu_devices.length - 1}
              <div class="px-2 border-l border-darkpurple text-darkpurple bg-surface-50 italic">{device}</div> 
            {:else}
              <div class="px-2 border-l border-darkpurple rounded-r-lg text-darkpurple bg-surface-50 italic">{device}</div> 
            {/if}
          {/each}
        </div>

      </div>
    </div>
  {/if}



  {#if card.datacard_uids.length > 0 || card.modelcard_uids.length > 0}

  <div class="flex flex-row items-center mb-2 pt-2 border-b-2 border-gray-400">
    <Fa icon={faFileContract} color="#04cd9b"/>
    <header class="pl-2 text-darkpurple text-lg font-bold">Cards</header>
  </div>

  <div class="flex flex-col space-y-1">

    {#if card.datacard_uids.length > 0}
      <MetadataPillList title="DataCards" uids={card.datacard_uids} type="data" />
    {/if}

    {#if card.modelcard_uids.length > 0}
      <MetadataPillList title="ModelCards" uids={card.modelcard_uids} type="model" />
    {/if}
  </div>
  {/if}
  
  <!-- tags -->
  {#if Object.keys(card.tags).length > 0}
    <div class="flex flex-row items-center mb-2 pt-2 border-b-2 border-gray-400">
      <Fa icon={faTag} color="#04cd9b"/>
      <header class="pl-2 text-darkpurple text-lg font-bold">Tags</header>
    </div>

    <div class="flex flex-col space-y-1">

      {#each Object.keys(card.tags) as key}

      <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
        <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">{key}</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
          {card.tags[key]}
        </div>
      </div>

      {/each}
    </div>
  {/if}
</div>

