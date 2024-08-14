<script lang="ts">

  import { type Card, type DataCardMetadata } from "$lib/scripts/types";
  import { loadModal } from "$lib";
  import Fa from 'svelte-fa'
  import { faTag, faFileContract, faCircleInfo } from '@fortawesome/free-solid-svg-icons'
  
  import { type ModalStore} from '@skeletonlabs/skeleton';
  import CodeModal from '$lib/components/CodeModal.svelte';
  import type { ModalComponent, ModalSettings } from '@skeletonlabs/skeleton';
  
  export let metadata: DataCardMetadata;
  export let card: Card;
  let registry: string = "data";
  
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
    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">ID</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {card.uid}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Name</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {card.name}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Repository</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {card.repository}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Version</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {card.version}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Data Interface</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.interface_type}
      </div>
    </div>
  </div>


  {#if card.runcard_uid !== null}
    <div class="flex flex-row items-center mb-2 pt-2 border-b-2 border-gray-400">
      <Fa icon={faFileContract} color="#04cd9b"/>
      <header class="pl-2 text-darkpurple text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-col space-y-1">
      <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
        <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">RunCard</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
          <a href="/opsml/run/card?uid={card.runcard_uid}" class="text-darkpurple">
            Link
          </a>
        </div>
      </div>
    </div>
  {/if}

   <!-- tags -->
  {#if Object.keys(card.tags).length > 0}
    <div class="flex flex-row items-center pt-2 border-b-2 border-gray-400">
      <Fa icon={faTag} color="#04cd9b"/>
      <header class="pl-2 text-darkpurple text-lg font-bold">Tags</header>
    </div>

    <div class="flex flex-col space-y-1">

      {#each Object.keys(card.tags) as key}
        <div class="inline-flex items-center overflow-hidden text-sm w-fit">
          <div class="px-2 text-darkpurple italic">{key}:</div> 
          <div class="flex px-1.5 text-gray-800">
            {card.tags[key]}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>