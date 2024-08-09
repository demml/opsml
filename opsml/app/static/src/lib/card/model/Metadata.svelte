<script lang="ts">

import { type ModelMetadata , type Card } from "$lib/scripts/types";
import Fa from 'svelte-fa'
import { faTag, faSquareCheck, faFileContract, faCircleInfo, faCheck } from '@fortawesome/free-solid-svg-icons'
import Highlight from "svelte-highlight";
import json from "svelte-highlight/languages/json";

import CodeModal from '$lib/components/CodeModal.svelte';
import { loadModal } from "$lib";
import type { ModalComponent, ModalSettings, ModalStore } from '@skeletonlabs/skeleton';

export let metadata: ModelMetadata;
export let card: Card;

const modalStore: ModalStore = loadModal();

async function showModal() {

  const modalComponent: ModalComponent = {
    ref: CodeModal,
    props: { 
      uid: card.uid,
      registry: "model",
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
      <button type="button" class="btn btn-sm bg-darkpurple text-white justify-end mb-2" on:click={() => showModal()}>Use this model</button>
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
        {metadata.model_name}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Repository</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.model_repository}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Model Interface</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.model_interface}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Task Type</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.task_type}
      </div>
    </div>


    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Model Type</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.model_type}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
      <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Opsml Version</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        {metadata.opsml_version}
      </div>
    </div>

    {#if metadata.onnx_version !== undefined}
      <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
        <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">Onnx Version</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
          {metadata.onnx_version}
        </div>
      </div>
    {/if}
  </div>


  {#if card.datacard_uid !== null || card.runcard_uid !== null}
    <div class="flex flex-row items-center mb-2 pt-2 border-b-2 border-gray-400">
      <Fa icon={faFileContract} color="#04cd9b"/>
      <header class="pl-2 text-darkpurple text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-col space-y-1">

      {#if card.datacard_uid !== null}
        <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
          <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">DataCard</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
            <a href="/opsml/data/card?uid={card.datacard_uid}" class="text-darkpurple">
              Link
            </a>
          </div>
        </div>
      {/if}

      {#if card.runcard_uid !== null}
        <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit">
          <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">RunCard</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
            <a href="/opsml/run/card?uid={card.runcard_uid}" class="text-darkpurple">
              Link
            </a>
          </div>
        </div>
      {/if}
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


  <!-- Add ons -->
  <div class="flex flex-row mb-2 items-center pt-2 border-b-2 border-gray-400">
    <Fa icon={faSquareCheck} color="#04cd9b"/>
    <header class="pl-2 text-darkpurple text-lg font-bold">Add Ons</header>
  </div>

  <div class="flex flex-wrap space-x-1 space-y-1 ">
    {#if metadata.preprocessor_uri !== undefined }

      <div class="inline-flex items-center overflow-hidden text-sm w-fit">
        <Fa icon={faCheck} color="darkpurple" class="pl-2"/> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
          preprocessor
        </div>
      </div>
    {/if}

    {#if metadata.onnx_uri !== undefined }
    <div class="inline-flex items-center overflow-hidden text-sm w-fit">
      <Fa icon={faCheck} color="darkpurple" class="pl-2"/> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        onnx model
      </div>
    </div>
    {/if}

    {#if metadata.quantized_model_uri !== undefined }
    <div class="inline-flex items-center overflow-hidden text-sm w-fit">
      <Fa icon={faCheck} color="darkpurple" class="pl-2"/> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        quantized model
      </div>
    </div>
    {/if}

    {#if metadata.tokenizer_uri !== undefined }
    <div class="inline-flex items-center overflow-hidden text-sm w-fit">
      <Fa icon={faCheck} color="darkpurple" class="pl-2"/> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        tokenizer
      </div>
    </div>
    {/if}

    {#if metadata.feature_extractor_uri !== undefined }
    <div class="inline-flex items-center overflow-hidden text-sm w-fit">
      <Fa icon={faCheck} color="darkpurple" class="pl-2"/> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        feature extractor
      </div>
    </div>
    {/if}
  </div>
</div>

<div class="rounded-lg border-2 border-darkpurple p-2 mb-2 shadow-md shadow-primary-500 bg-white">

  <div class="flex flex-row mb-2 items-center pt-2 border-b-2 border-gray-400">
    <Fa icon={faCircleInfo} color="#04cd9b"/>
    <header class="pl-2 text-darkpurple text-lg font-bold">Data Schema</header>
  </div>

  <div class="max-h-96 overflow-scroll text-sm">

    <Highlight language={json}  code={JSON.stringify(metadata.data_schema, null, 2)} let:highlighted>
    </Highlight>
  </div>

</div>