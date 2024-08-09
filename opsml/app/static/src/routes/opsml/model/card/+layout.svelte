<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag, faFolderTree, faCodeBranch, faBolt, faGears, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'
  import modelcard_circuit from '$lib/images/modelcard-circuit.svg'
  import { goto } from '$app/navigation';



  /** @type {import('./$types').LayoutData} */
	export let data;

  let registry: string = data.registry;

  let name: string = data.name;

  let repository: string = data.repository;

  let version: string = data.version;

  let tabSet: string = data.tabSet;

  let icon: string = modelcard_circuit;


  async function showTabContent(value: string ) {
    let baseURL: string = `/opsml/${registry}/card`;

    if (value === 'card') {
      goto(`${baseURL}?name=${name}&repository=${repository}&version=${version}`);
    } else if (value === 'versions') {
      goto(`${baseURL}/${value}?name=${name}&repository=${repository}&registry=${registry}&version=${version}`);

    }
    else {
      goto(`${baseURL}/${value}?name=${name}&repository=${repository}&version=${version}`);
    }

  }


</script>

<div class="flex flex-1 flex-col">

  <div class="pl-4 md:pl-20 pt-6 sm:pt-8 bg-slate-50 w-full border-b">
    <h1 class="flex flex-row flex-wrap items-center text-xl">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
      <div class="pl-2">
        <a href="/opsml/{registry}/card?name={name}&repository={repository}&version={version}" class="badge h-7 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
          <Fa class="h-4" icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{version}</span>
        </a>
      </div>
    </h1>

    <div class="pt-2">
      <TabGroup 
        border=""
        active='border-b-2 border-primary-500'
        >
          <Tab bind:group={tabSet} name="card" value="card" on:click={() => showTabContent("card")}>
            <div class="flex flex-row  items-center">
              <img class="h-6" src={icon} alt="ModelCard Circuit" />
              <div class="font-semibold">Card</div>
            </div>
          </Tab>
          <Tab bind:group={tabSet} name="files" value="files" on:click={() => showTabContent("files")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faFolderTree} color="#4b3978"/>
              <div class="font-semibold">Files</div>
            </div>
          </Tab>
          <Tab bind:group={tabSet} name="metadata" value="metadata" on:click={() => showTabContent("metadata")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faBolt} color="#4b3978"/>
              <div class="font-semibold">Metadata</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="versions" value="versions" on:click={() => showTabContent("versions")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faCodeBranch} color="#4b3978"/>
              <div class="font-semibold">Versions</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="monitoring" value="monitoring" on:click={() => showTabContent("monitoring")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faMagnifyingGlass} color="#4b3978"/>
              <div class="font-semibold">Monitoring</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="settings" value="settings" on:click={() => showTabContent("settings")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faGears} color="#4b3978"/>
              <div class="font-semibold">Settings</div>
            </div>
          </Tab>

          <Tab bind:group={tabSet} name="settings" value="settings" on:click={() => showTabContent("messages")}>
            <div class="flex flex-row  items-center">
              <Fa class="h-5 mr-2" icon={faGears} color="#4b3978"/>
              <div class="font-semibold">Messages/Notes</div>
            </div>
          </Tab>

        </TabGroup>

    </div>

  </div>
  <slot>
  </slot>
</div>
