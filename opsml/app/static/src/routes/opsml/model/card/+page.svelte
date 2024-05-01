<script lang="ts">

  import { type ModelMetadata , type Card } from "$lib/scripts/types";
  import Fa from 'svelte-fa'
  import { faTag, faSquareCheck, faFileContract, faCircleInfo, faCheck } from '@fortawesome/free-solid-svg-icons'
  import icon from '$lib/images/opsml-green.ico'
  import { goto } from '$app/navigation';
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import Markdown from "$lib/card/Markdown.svelte";
  import { clipboard } from '@skeletonlabs/skeleton';
  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";

  import { getModalStore } from '@skeletonlabs/skeleton';
			
  const modalStore = getModalStore();

  const modal: ModalSettings = {
	type: 'prompt',
	// Data
	title: 'Enter Name',
	body: 'Provide your first name in the field below.',
	// Populates the input value and attributes
	value: 'Skeleton',
	valueAttr: { type: 'text', minlength: 3, maxlength: 10, required: true },
	// Returns the updated response value
	response: (r: string) => console.log('response:', r),
  };
  


	/** @type {import('./$types').LayoutData} */
	export let data;

  let hasReadme: boolean;
  $: hasReadme = data.hasReadme;

  let readme: string;
  $: readme = data.readme;

  let metadata: ModelMetadata;
  $: metadata = data.metadata;

  let card: Card;
  $: card = data.card;

  let uid: string;
  $: uid = card.uid;

  async function createReadme() {
    let baseURL: string = `/opsml/model/card/readme`;

     goto(`${baseURL}?name=${metadata.model_name}&repository=${metadata.model_repository}&version=${metadata.model_version}&status=edit`);
   

  }


  async function showModal() {
    modalStore.trigger(modal);
  }

</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>
<button type="button" class="btn variant-filled" on:click={() => showModal()}>Modal</button>

<div class="flex flex-wrap bg-white min-h-screen mb-8">
  <div class="w-full md:w-3/5 mt-4 ml-4 pl-2 md:ml-12 shadow-md">
    {#if !hasReadme}
        <div class="mt-5 mx-5 py-24 bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
          <p class="mb-1">No card README found</p>
          <p class="mb-1 text-sm text-gray-500">Click button below to create a README!</p>
          <p class="mb-6 text-sm text-gray-500">Note: README applies to all versions of a given model and repository </p>
          <button type="button" class="btn variant-filled" on:click={() => createReadme()}>
            <img class="h-5" alt="The project logo" src={icon} />
            <span>Create</span>
          </button>
        </div>
        {:else}
        <div class="mt-2 mr-5">
          <div class="flex rounded-t-lg px-3 min-w-96 justify-end ">
            <div>
              <button type="button" class="btn btn-sm bg-primary-500 text-white" on:click={() => { createReadme() }}>
                <span>Edit Readme</span>
              </button>
            </div>
          </div>
          <Markdown 
              source={readme}
              globalPadding='5px'
              globalPaddingMobile='0px'  
          />
        </div>
      {/if}
  </div>
  <div class="flex flex-col w-full md:w-1/3">
    <div class="p-4">
      <div class="rounded-lg border-2 border-darkpurple p-4 shadow-md mb-2">
    
        <div class="flex flex-row mb-2 items-center pt-2 border-b-2 border-gray-400">
          <Fa icon={faCircleInfo} color="#04cd9b"/>
          <header class="pl-2 text-darkpurple text-lg font-bold">Metadata</header>
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

      <div class="rounded-lg border-2 border-darkpurple p-2 shadow-md mb-2">
    
        <div class="flex flex-row mb-2 items-center pt-2 border-b-2 border-gray-400">
          <Fa icon={faCircleInfo} color="#04cd9b"/>
          <header class="pl-2 text-darkpurple text-lg font-bold">Data Schema</header>
        </div>

      <div class="max-h-96 overflow-scroll">

        <Highlight language={json}  code={JSON.stringify(metadata.data_schema, null, 2)} let:highlighted>
        </Highlight>
      </div>


      </div>
    </div>
  </div>
</div>
        

       

  