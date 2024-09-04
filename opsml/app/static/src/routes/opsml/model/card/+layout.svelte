<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag, faFolderTree, faCodeBranch, faBolt, faGears, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'
  import modelcard_circuit from '$lib/images/modelcard-circuit.svg'
  import { goto } from '$app/navigation';
  import type { Card } from "$lib/scripts/types";
  import { onMount } from 'svelte';
  import { page } from '$app/stores';


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

  let hasReadme: boolean;
  $: hasReadme = data.hasReadme;

  let tabSet: string;
  $: tabSet = "home";


  async function showTabContent(value: string ) {
    let baseURL: string = `/opsml/${registry}/card`;

    goto(`${baseURL}/${value}?name=${name}&repository=${repository}&version=${card.version}`,  { invalidateAll: false });


    tabSet = value;

  }


  onMount(() => {
    if ($page.url.pathname.includes("files")) {
        tabSet = "files";
    }
    else if ($page.url.pathname.includes("metadata")) {
        tabSet = "metadata";
    }
    else if ($page.url.pathname.includes("versions")) {
        tabSet = "versions";
    }
    else if ($page.url.pathname.includes("monitoring")) {
        tabSet = "monitoring";
    }
    else if ($page.url.pathname.includes("settings")) {
        tabSet = "settings";
    }
    else if ($page.url.pathname.includes("messages")) {
        tabSet = "messages";
    }
    else {
      tabSet = "home";
    }
  });


 

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
          <Tab bind:group={tabSet} name="metadata" value="metadata" on:click={() => showTabContent("metadata")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-1" icon={faBolt} color="#4b3978"/>
              <div class="font-semibold text-sm">Metadata</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="versions" value="versions" on:click={() => showTabContent("versions")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-1" icon={faCodeBranch} color="#4b3978"/>
              <div class="font-semibold text-sm">Versions</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="monitoring" value="monitoring" on:click={() => showTabContent("monitoring")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-1" icon={faMagnifyingGlass} color="#4b3978"/>
              <div class="font-semibold text-sm">Monitoring</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="settings" value="settings" on:click={() => showTabContent("settings")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-1" icon={faGears} color="#4b3978"/>
              <div class="font-semibold text-sm">Settings</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="settings" value="settings" on:click={() => showTabContent("messages")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-4 mr-1" icon={faGears} color="#4b3978"/>
              <div class="font-semibold text-sm">Messages/Notes</div>
            </div>
          </Tab>

        </TabGroup>

    </div>

  </div>
  <slot>
  </slot>
</div>
