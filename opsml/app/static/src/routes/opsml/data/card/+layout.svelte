<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag, faFolderTree, faCodeBranch, faBolt, faGears, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'
  import modelcard_circuit from '$lib/images/modelcard-circuit.svg'
  import { goto } from '$app/navigation';
  import type { Card, DataCardMetadata } from "$lib/scripts/types";



  /** @type {import('./$types').LayoutData} */
	export let data;

  let registry: string;
  $: registry = data.registry;

  let name: string;
  $: name = data.name;

  let repository: string;
  $: repository = data.repository;

  let card: Card;
  $: card = data.card;

  let tabSet: string;
  $: tabSet = "home";

  let metadata: DataCardMetadata;
  $: metadata = data.metadata;


  async function showTabContent(value: string ) {
    let baseURL: string = `/opsml/${registry}/card`;

    goto(`${baseURL}/${value}?name=${name}&repository=${repository}&version=${card.version}`,  { invalidateAll: false });


    tabSet = value;

  }

</script>

<div class="flex flex-1 flex-col">

  <div class="pl-4 md:pl-20 pt-2 sm:pt-4 bg-slate-50 w-full border-b">
    <h1 class="flex flex-row flex-wrap items-center text-lg">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
      <div class="pl-2">
        <a href="/opsml/{registry}/card/home?name={name}&repository={repository}&version={card.version}" class="badge h-7 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
          <Fa class="h-4" icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{card.version}</span>
        </a>
      </div>
    </h1>

    <div class="pt-1">
      <TabGroup 
        padding="px-3 py-2"
        border=""
        active='border-b-2 border-primary-500'
        >
          <Tab bind:group={tabSet} name="home" value="home" on:click={() => showTabContent("home")}>
            <div class="flex flex-row items-center">
              <img class="h-4" src={modelcard_circuit} alt="ModelCard Circuit" />
              <div class="font-semibold text-sm">Card</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="files" value="files" on:click={() => showTabContent("files")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faFolderTree} color="#4b3978"/>
              <div class="font-semibold text-sm">Files</div>
            </div>
          </Tab>

          {#if metadata.data_splits}
            <Tab bind:group={tabSet} name="splits" value="splits" on:click={() => showTabContent("splits")}>
              <div class="flex flex-row  items-center">
                <Fa class="h-4 mr-2" icon={faBolt} color="#4b3978"/>
                <div class="font-semibold text-sm">Splits</div>
              </div>
            </Tab>
          {/if}

          <Tab bind:group={tabSet} name="versions" value="versions" on:click={() => showTabContent("versions")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-2" icon={faCodeBranch} color="#4b3978"/>
              <div class="font-semibold text-sm">Versions</div>
            </div>
          </Tab>

          {#if metadata.sql_logic}
            <Tab bind:group={tabSet} name="sql" value="sql" on:click={() => showTabContent("sql")}>
              <div class="flex flex-row  items-center">
                <Fa class="h-4 mr-2" icon={faGears} color="#4b3978"/>
                <div class="font-semibold text-sm">SQL</div>
              </div>
            </Tab>
          {/if}

        </TabGroup>

    </div>

  </div>
  <slot>
  </slot>
</div>
