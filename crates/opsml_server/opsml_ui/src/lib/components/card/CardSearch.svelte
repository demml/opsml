<script lang="ts">

  import { Switch } from '@skeletonlabs/skeleton-svelte';
  import CardTableView from "$lib/components/card/CardTableView.svelte";
  import { onMount } from "svelte";
  import type { RegistryPageReturn, RegistryStatsResponse, QueryPageResponse} from "$lib/components/card/types";
  import  { RegistryType, delay, getRegistryTypeUpperCase } from "$lib/utils";
  import { ArrowLeft, ArrowRight, Settings } from 'lucide-svelte';
  import { getRegistryPage, getRegistryStats } from '$lib/components/api/registry';
  import { Combobox } from "melt/builders";
  import CardPage from '$lib/components/card/CardPage.svelte';
  import MultiComboBoxDropDown from '$lib/components/utils/MultiComboBoxDropDown.svelte';

  let { page, selectedName, selectedSpace } = $props<{
    page: RegistryPageReturn;
    selectedName: string | undefined;
    selectedSpace: string | undefined;
  }>();
 
  let viewState = $state(true);
  let currentPage = $state(1);
  let totalPages = $state(1);
  let artifactSearchQuery = $state(selectedName || '');

  let filteredSpaces: string[] = $state([]);
  let filteredTags: string[] = $state([]);

  let registryType = $state<RegistryType>(page.registry_type);
  let registryPage = $state<QueryPageResponse>(page.registryPage);
  let registryStats = $state<RegistryStatsResponse>(page.registryStats);
  let artifactTitle = $state<string>(`${getRegistryTypeUpperCase(registryType)} Artifacts`);


  let availableSpaces = page.spaces;
  let availableTags = page.tags;


  onMount(() => {
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);

    // if selectedSpace is defined, add it to filteredSpaces and spacesCombobox
    if (selectedSpace && !filteredSpaces.includes(selectedSpace)) {
      filteredSpaces = [...filteredSpaces, selectedSpace];
    }

  });

  let searchTimeout: ReturnType<typeof setTimeout> | null = null;

  function onInputChange() {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      await searchPage();
    }, 100);
  }

  // effect to run SearchPage when filteredSpaces changes
  $effect(() => {
    if (filteredSpaces.length > 0 ||  filteredTags.length > 0) {
      onInputChange();
    }
  });

  const searchPage = async function () {
  [registryPage, registryStats] = await Promise.all([ 
    getRegistryPage(fetch, registryType, undefined, filteredSpaces, artifactSearchQuery, filteredTags, 1), 
    getRegistryStats(fetch, registryType, artifactSearchQuery, filteredSpaces, filteredTags)
  ]);
  currentPage = 1;
  totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }

  const changePage = async function (page: number) {
    registryPage = await getRegistryPage(fetch, registryType, undefined, filteredSpaces, artifactSearchQuery, filteredTags, page);
    currentPage = page;
  }

</script>




<div class="flex flex-col mx-auto w-11/12 pt-4 px-4 pb-10">
  <div class="inline-flex items-center bg-surface-50 border-black border-2 shadow-small mb-4 px-3 py-2 rounded-2xl self-start">
    <p class="mr-2 font-bold text-primary-800">Table View</p>
    <Switch 
      name="viewSwitch" 
      checked={viewState} 
      thumbInactive="bg-primary-500"
      thumbActive="bg-white"
      controlActive="bg-primary-500 border-black border-1"
      controlInactive="bg-white border-black border-1"
      onCheckedChange={(e) => (viewState = e.checked)}
    >
    </Switch>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
    <div class="col-span-1 lg:col-span-1 p-2 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 self-start overflow-hidden">
    <!-- Top Section -->
      <MultiComboBoxDropDown
        boxId="space-search-input"
        label="Search Spaces"
        bind:filteredItems={filteredSpaces}
        availableOptions={availableSpaces}
        defaultSelected={selectedSpace ? [selectedSpace] : []}
      />

      <hr class="hr" />
      
      <MultiComboBoxDropDown
        boxId="tag-search-input"
        label="Search Tags"
        bind:filteredItems={filteredTags}
        availableOptions={availableTags}
      />
    </div>
  
    <div class="col-span-1 lg:col-span-4 gap-1 p-4 flex-1 flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 h-auto">
      <div class="flex flex-row items-center gap-2 pb-2">
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <Settings color="#40328b" />
        </div>
        <h2 class="font-bold text-primary-800 text-lg">{artifactTitle}</h2>
      </div>

      <div class="flex flex-row flex-wrap gap-1 items-center ml-1">
        <div>
          <span class="badge text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_names} artifacts</span>
        </div>
        <div>
          <span class="badge text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_versions} versions</span>
        </div>
        <div>
          <span class="badge text-primary-800 border-black border-1 shadow-small bg-surface-50">{registryStats.stats.nbr_spaces} spaces</span>
        </div>
        <div class=" w-full md:w-auto lg:flex-1">
          <input
            class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-1 border-black border-2 h-9"
            type="text"
            bind:value={artifactSearchQuery}
            placeholder="Search artifacts"
            onkeydown={delay(searchPage, 1000)}
          />
        </div>
      </div>

      {#if viewState}
        <CardTableView registry={registryType} registryPage={registryPage} />
      {:else}

        <div class="pt-4 grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-2 justify-items-center">
          {#each registryPage.summaries as summary}
              <CardPage
                space={summary.space}
                name={summary.name}
                version={summary.version}
                nbr_versions={summary.versions}
                updated_at={summary.updated_at}
                registry={registryType}
                bgColor={"bg-primary-400"}
              />
          {/each}
        </div>
      {/if}
      
      <div class="flex justify-center pt-4 gap-2">
        {#if currentPage > 1}
          <button class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9" onclick={() => changePage(currentPage - 1)}>
            <ArrowLeft color="#5948a3"/>
          </button>
        {/if}
        <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
          <span class="text-primary-800 mr-1 text-xs">{currentPage}</span>
          <span class="text-primary-400 text-xs">of {totalPages}</span>
        </div>
        {#if currentPage < totalPages }
          <button class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9" onclick={() => changePage(currentPage + 1)}>
            <ArrowRight color="#5948a3"/>
          </button>
        {/if}
      </div>

    </div>
  </div>
</div>