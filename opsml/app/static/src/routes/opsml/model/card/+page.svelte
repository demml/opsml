<script lang="ts">

  import { type ModelMetadata , type Card } from "$lib/scripts/types";
  import Fa from 'svelte-fa'
  import { faTag, faIdCard, faFolderOpen, faBrain, faFile, faLink } from '@fortawesome/free-solid-svg-icons'
  import icon from '$lib/images/opsml-green.ico'
  import { goto } from '$app/navigation';
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import Markdown from "$lib/card/Markdown.svelte";


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

  async function createReadme() {
    let baseURL: string = `/opsml/model/card/readme`;

     goto(`${baseURL}?name=${metadata.model_name}&repository=${metadata.model_repository}&status=edit`);
   

  }

</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex flex-wrap bg-white min-h-screen">
  <div class="w-full md:w-3/5 border-r border-grey-100 pl-4 md:pl-20">
    {#if !hasReadme}
      <div class="mt-5 mr-5 py-24 bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
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
  <div class="flex flex-col w-full md:w-1/3 mt-5">
    <div class="pl-4">
      <header class="mb-2 text-lg font-bold">Metadata</header>

      <!-- UID -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">ID:</div>
        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {card.uid}
          </div>
        </div>
      </div>

      <!-- name -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Name:</div>
        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {metadata.model_name}
          </div>
        </div>
      </div>

      <!-- version -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Version:</div>
        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {metadata.model_version}
          </div>
        </div>
      </div>

      <!-- repository -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faFolderOpen} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Respository:</div>

        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {metadata.model_repository}
          </div>
        </div>
      </div>

      <!-- model interface -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faBrain} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Model Interface:</div>
        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {metadata.model_interface}
          </div>
        </div>
      </div>

      <!-- model type -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faFile} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Model Type:</div>
        <div class="w-48 ">
          <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
            {metadata.model_type}
          </div>
        </div>
      </div>

      <!-- datacard -->
      {#if card.datacard_uid !== null}
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faLink} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">DataCard:</div>
          <div class="w-48 ">
            <div>
              <a href="/opsml/data/card?uid={card.datacard_uid}" class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
              Link
              </a>
            </div>
          </div>
        </div>
      {/if}

      <!-- Runcard -->
      {#if card.runcard_uid !== null}
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faLink} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">RunCard:</div>
          <div class="w-48 ">
            <div>
              <a href="/opsml/run/card?uid={card.runcard_uid}" class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
              Link
              </a>
            </div>
          </div>
        </div>
      {/if}
    </div>

    <div class="border-t mt-1">

      <div class="pl-4">
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faTag} color="#04cd9b"/>
          </div>
          <header class="my-1 text-gray-500 text-lg font-bold">Tags</header>
        </div>

        <!-- tags -->
        {#if Object.keys(card.tags).length > 0}
          {#each Object.keys(card.tags) as key}
            <div class="flex flex-row gap-1 items-center">
              <div class="w-32 font-semibold text-gray-500">{key}</div>
              <div class="w-48 ">
                <div class="badge h-6 border text-primary-500 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
                  {card.tags[key]}
                </div>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>


  </div>
  
</div>