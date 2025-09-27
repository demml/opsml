
<script lang="ts">
  import { onMount } from "svelte";
  import { getRegistryPage, getRegistryStats, getBgColor, resolveCardPathFromArgs } from "./utils";
  import type { RegistryPageReturn, RegistryStatsResponse, QueryPageResponse} from "$lib/components/card/types";
  import  { RegistryType, delay, getRegistryTypeUpperCase } from "$lib/utils";
  import { ArrowLeft, ArrowRight, Search, Settings } from 'lucide-svelte';
  import { Combobox } from "melt/builders";
  import { goto } from "$app/navigation";
  
  let { selectedSpace, page, selectedName, title } = $props<{
    selectedSpace: string | undefined;
    selectedName: string | undefined;
    page: RegistryPageReturn;
    title: RegistryType;
  }>();
 
  let currentPage = $state(1);
  let totalPages = $state(1);


  let artifactSearchQuery = $state(selectedName || '');
  let activeSpace = $state<string | undefined>(selectedSpace);


  let availableSpaces = page.spaces;
  let availableTags = page.tags;

  let filteredSpaces: string[] | undefined = $state(undefined);
  let filteredTags: string[] | undefined = $state(undefined);


  // registry-specific state
  let registryType = $state<RegistryType>(page.registry_type);
  let registryPage = $state<QueryPageResponse>(page.registryPage);
  let registryStats = $state<RegistryStatsResponse>(page.registryStats);
  let artifactTitle = $state<string>(`${getRegistryTypeUpperCase(title)} Artifacts`);

  type Option = (typeof availableSpaces)[string];

  //@ts-ignore
  const spacesCombobox = new Combobox<string>({ multiple: true });

  //@ts-ignore
  const tagsCombobox = new Combobox<string>({ multiple: true, onValueChange: onTagsChange });




  onMount(() => {
  
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);

  });

  async function setActiveRepo(space: string) {

    // handle click and declick
    if (activeSpace === space) {
      activeSpace = undefined;
    } else {
      activeSpace = space;
    }

    registryPage = await getRegistryPage(registryType, undefined, activeSpace, undefined, undefined, 1);
    registryStats = await getRegistryStats(registryType, activeSpace);
    currentPage = 1;
    totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }


  let tagSearchTimeout: ReturnType<typeof setTimeout> | null = null;

  
  function onTagsChange() {
    if (tagSearchTimeout) clearTimeout(tagSearchTimeout);
    tagSearchTimeout = setTimeout(async () => {
      // set filteredTags based on tagsCombobox.value
      //@ts-ignore
      // tagsCombobox.value is an object. Need to convert to array of strings
      filteredTags = [...tagsCombobox.value] as string[];



      // Call your searchPage function, passing selectedTags if needed
      //await searchPage(selectedTags);
    }, 100);
  }


  const searchPage = async function () {
  registryPage = await getRegistryPage(registryType, undefined, activeSpace, artifactSearchQuery, filteredTags, 1);
  registryStats = await getRegistryStats(registryType, artifactSearchQuery, activeSpace, filteredTags);
  currentPage = 1;
  totalPages = Math.ceil(registryStats.stats.nbr_names / 30);
  }

  const changePage = async function (page: number) {
    registryPage = await getRegistryPage(registryType, undefined, activeSpace, artifactSearchQuery, undefined, page);
    registryStats = await getRegistryStats(registryType, artifactSearchQuery, activeSpace);
    currentPage = page;
  }

  function navigateToCardPage(registry: RegistryType, space: string, name: string, version: string) {
      let path = resolveCardPathFromArgs(registry, space, name, version);
      goto(path);
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


<div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
  <!-- Left column -->
  <div class="col-span-1 lg:col-span-1 p-2 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 self-start">
    <!-- Top Section -->
    <div class="mb-4 text-black flex flex-col items-center max-w-xs">
      <div class="flex flex-col items-start">
        <label {...spacesCombobox.label} class="text-primary-800 mb-1">Search Spaces</label>
        <input {...spacesCombobox.input} class="space-input bg-primary-100 text-black border-black border-2 rounded-lg"/>
      </div>
      <div {...spacesCombobox.content} class="bg-primary-100 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1">
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
    </div>

    <hr class="hr" />

    <div class="my-2 text-black flex flex-col items-center max-w-xs">
      <div class="flex flex-col items-start">
        <label {...tagsCombobox.label} class="text-primary-800 mb-1">Search Tags</label>
        <input 
          {...tagsCombobox.input} 
          class="tag-input bg-primary-100 text-black border-black border-2 rounded-lg"
        />
      </div>
      <div {...tagsCombobox.content} class="bg-primary-100 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1">
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
        {#each tagsCombobox.value as tag (tag)}
          <span class="badge bg-primary-100 text-primary-800">{tag}</span>
        {/each}
      </div>
    </div>


  </div>

  <!-- Right column -->
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

    <div class="pt-4">
        <div class="overflow-auto w-full border-2 border-black rounded-lg">
          <table class="text-black border-collapse text-sm bg-white w-full">
            <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
              <tr>
                <th class="p-2 font-heading pl-6 text-left text-black">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Space
                  </span>
                </th>
                <th class="p-2 font-heading">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Name
                  </span>
                </th>
                <th class="p-2 font-heading">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Last Updated
                  </span>
                </th>
                <th class="p-2 font-heading">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Current Version
                  </span>
                </th>
                <th class="p-2 font-heading">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Versions
                  </span>
                </th>
                <th class="p-2 font-heading">
                  <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                    Link
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
          {#each registryPage.summaries as summary, i}
            <tr class={`border-b-2 border-black hover:bg-primary-300 ${i % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
              <td class="p-2 pl-8">{summary.space}</td>
              <td class="p-2 text-center">{summary.name}</td>
              <td class="p-2 text-center">{summary.updated_at}</td>
              <td class="p-2 text-center">{summary.version}</td>
              <td class="p-2 text-center">{summary.versions}</td>
              <td class="p-2">
                <button class="btn text-sm flex flex-row gap-1 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => navigateToCardPage(registryType, summary.space, summary.name, summary.version)}>
                  <div class="text-black">Link</div>
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
          </table>
        </div>
    </div>

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
