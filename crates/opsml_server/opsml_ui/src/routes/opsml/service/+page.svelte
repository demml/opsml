<script lang="ts">

  import type { PageProps } from './$types';
  import { Switch } from '@skeletonlabs/skeleton-svelte';
  import CardTableView from "$lib/components/card/CardTableView.svelte";
  import { onMount } from "svelte";
  import { getRegistryPage, getRegistryStats} from "$lib/components/card/utils";
  import type { RegistryPageReturn, RegistryStatsResponse, QueryPageResponse} from "$lib/components/card/types";
  import  { RegistryType, delay, getRegistryTypeUpperCase } from "$lib/utils";
  import { ArrowLeft, ArrowRight, Search, Settings } from 'lucide-svelte';
  import { Combobox } from "melt/builders";
  import CardPage from '$lib/components/card/CardPage.svelte';

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedName: string | undefined = data.selectedName;
  let selectedSpace: string | undefined = data.selectedSpace;
  let viewState = $state(true);

  let currentPage = $state(1);
  let totalPages = $state(1);
  let artifactSearchQuery = $state(selectedName || '');
  let filteredSpaces: string[] = $state([]);
  let filteredTags: string[] = $state([]);

  let registryType = $state<RegistryType>(page.registry_type);
  let registryPage = $state<QueryPageResponse>(page.registryPage);
  let registryStats = $state<RegistryStatsResponse>(page.registryStats);
  let artifactTitle = $state<string>(`${getRegistryTypeUpperCase(data.registryType)} Artifacts`);


  let availableSpaces = page.spaces;
  let availableTags = page.tags;

  //@ts-ignore
  const spacesCombobox = new Combobox<string>({ multiple: true, onValueChange: onSpaceChange });
  //@ts-ignore
  const tagsCombobox = new Combobox<string>({ multiple: true, onValueChange: onTagsChange });

  onMount(() => {
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);

    // if selectedSpace is defined, add it to filteredSpaces and spacesCombobox
    if (selectedSpace && !filteredSpaces.includes(selectedSpace)) {
      filteredSpaces = [...filteredSpaces, selectedSpace];
      spacesCombobox.select(selectedSpace);
    }
    
  });


  let searchTimeout: ReturnType<typeof setTimeout> | null = null;
  function onTagsChange() {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      // set filteredTags based on tagsCombobox.value
      //@ts-ignore
      filteredTags = [...tagsCombobox.value] as string[];
      await searchPage();
    }, 100);
  }

  function onSpaceChange() {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      // set filteredSpaces based on spacesCombobox.value
      //@ts-ignore
      filteredSpaces = [...spacesCombobox.value] as string[];
      await searchPage();
    }, 100);
  }

  const searchPage = async function () {
  [registryPage, registryStats] = await Promise.all([ 
    getRegistryPage(registryType, undefined, filteredSpaces, artifactSearchQuery, filteredTags, 1), 
    getRegistryStats(registryType, artifactSearchQuery, filteredSpaces, filteredTags)
  ]);
  currentPage = 1;
  totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }

  const changePage = async function (page: number) {
    registryPage = await getRegistryPage(registryType, undefined, filteredSpaces, artifactSearchQuery, filteredTags, page);
    currentPage = page;
  }

</script>

<style>
  .space-input {
    height: 2.0rem;
  }

  .space-input:focus {
    height: 2.0rem;
    box-shadow: 0 0 0 3px oklch(69.32% 0.15 294.6deg);
  }

  .tag-input {
    height: 2.0rem;
  }

  .tag-input:focus {
    height: 2.0rem;
    box-shadow: 0 0 0 3px oklch(69.32% 0.15 294.6deg);
  }

</style>



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
      <div class="mb-4 text-black flex flex-col items-center w-full relative">
        <div class="flex flex-col items-start w-full">
          <label {...spacesCombobox.label} class="text-primary-800 mb-1">Search Spaces</label>
          <input {...spacesCombobox.input} class="space-input bg-primary-100 text-black border-black border-2 rounded-lg w-full"/>
        </div>
        <div {...spacesCombobox.content} class="bg-primary-100 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1 w-full">
          {#each availableSpaces as option (option)}
            <div {...spacesCombobox.getOption(option)} class="px-2 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black">
              {option}
              {#if spacesCombobox.isSelected(option)}
                ✓
              {/if}
            </div>
          {:else}
            <span>No results found</span>
          {/each}
        </div>

        <!--Show filtered spaces as pills-->
        <div class="mt-2 flex flex-wrap gap-1 items-start">
          {#each filteredSpaces as space}
          <button
            class="badge bg-primary-100 text-primary-800 flex items-center gap-1 px-2 py-1"
            onclick={() => spacesCombobox.select(space)}
            aria-label={`Deselect space ${space}`}
            type="button"
          >
            <span>{space}</span>
            <span class="ml-1 text-lg font-bold" aria-hidden="true">&times;</span>
          </button>
          {/each}
        </div>

      </div>
      <hr class="hr" />
      <div class="my-2 text-black flex flex-col items-center w-full relative">
        <div class="flex flex-col items-start w-full">
            <label {...tagsCombobox.label} class="text-primary-800 mb-1">Search Tags</label>
            <input 
            {...tagsCombobox.input} 
            class="tag-input bg-primary-100 text-black border-black border-2 rounded-lg w-full"
            />
        </div>
        <div {...tagsCombobox.content} class="bg-primary-100 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1 w-full">
            {#each availableTags as option (option)}
            <div {...tagsCombobox.getOption(option)} class="px-2 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black">
                {option}
                {#if tagsCombobox.isSelected(option)}
                ✓
                {/if}
            </div>
            {:else}
            <span>No results found</span>
            {/each}
        </div>
        <!--Show filtered tags as pills-->
        <div class="mt-2 flex flex-wrap gap-1 items-start">
          {#each filteredTags as tag}
          <button
            class="badge bg-primary-100 text-primary-800 flex items-center gap-1 px-2 py-1"
            onclick={() => tagsCombobox.select(tag)}
            aria-label={`Deselect tag ${tag}`}
            type="button"
          >
            <span>{tag}</span>
            <span class="ml-1 text-lg font-bold" aria-hidden="true">&times;</span>
          </button>
          {/each}
        </div>
      </div>
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