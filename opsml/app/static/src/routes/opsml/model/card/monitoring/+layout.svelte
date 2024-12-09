<script lang="ts">

  import { type SpcDriftProfile, TimeWindow, ProfileType } from "$lib/scripts/types";
  import logo from '$lib/images/opsml-green.ico';
  import scouter_logo from '$lib/images/scouter.svg';
  import Dropdown from "$lib/components/Dropdown.svelte";
  import SpcProfile from "$lib/card/monitoring/SpcProfile.svelte";
  import { goto } from '$app/navigation';
  import type { RouteVizData } from "$lib/scripts/monitoring/utils";
  import Observability from "$lib/card/monitoring/Observability.svelte";
  import { Autocomplete, popup  } from '@skeletonlabs/skeleton';
  import type { AutocompleteOption, PopupSettings } from '@skeletonlabs/skeleton';
  import { onMount } from "svelte";

  /** @type {import('./$types').LayoutData} */
  export let data;

  let repository: string;
  repository = data.repository;

  let name: string;
  name = data.name;

  let version: string;
  version = data.version;

  let driftProfiles: Map<ProfileType, SpcDriftProfile>;
  driftProfiles = data.driftProfiles;

  let targetFeature: string;
  $: targetFeature = data.feature;

  let features: string[];
  $: features = data.features;

  let showConfig: boolean;
  $: showConfig = data.showConfig;

  let timeWindow: string;
  $: timeWindow = data.timeWindow;

  let profileType: ProfileType;
  $: profileType = data.type;

  let routeViz: RouteVizData[];
  routeViz = data.routeViz;

  let max_data_points: number;
  max_data_points = data.max_data_points;

  let timeWindows: string[] = Object.values(TimeWindow);

  async function navigate() {
    let baseURL: string = `/opsml/model/card/monitoring/feature`;
    goto(`${baseURL}?name=${name}&repository=${repository}&version=${version}&feature=${targetFeature}&type=${profileType}&time=${timeWindow}`,  { invalidateAll: false, noScroll: true });
  }


  async function handleTimeWindowChange(event) {
      timeWindow = event.detail.selected;
      await navigate();
  }

  function toggleProfile() {
    showConfig = !showConfig;
  }

  async function updateFeatureValues(event: CustomEvent<FlavorOption>) {
    let feature = event.detail.label;

    if (feature === targetFeature) {
      return;
    }

    targetFeature = feature;
    await navigate();

  }

  function handleUpdate(event) {
      showConfig = event.detail.showConfig;
      driftProfiles[profileType].config = event.detail.updatedDriftConfig;
    }

  function handleHide(event) {
    showConfig = event.detail.showConfig;
  }

  type FlavorOption = AutocompleteOption<string, { healthy: boolean }>;

  function getFlavorOptions(): FlavorOption[] {
    return features.map((featureName) => {
      return { label: featureName, value: featureName, keywords: featureName, meta: { healthy: false } };
    });
  }


  let popupSettings: PopupSettings = {
    event: 'focus-click',
    target: 'popupAutocomplete',
    placement: 'bottom',
  };

  let flavorOptions: FlavorOption[]

  onMount(() => {
    flavorOptions= getFlavorOptions();
  });
  


  let selected: string = targetFeature;


</script>

<main>
  <div class="flex min-h-screen overflow-x-scroll bg-white">
    {#if driftProfiles}
      
      <div class="flex-col pt-4 w-full px-12">

        <!--Drift Header with dropdown-->
        <div class="flex justify-between">
          <div class="flex justify-between">
            <img alt="Scouter logo" class="h-9 mx-1 self-center" src={scouter_logo}>
            <div class="text-primary-500 text-xl font-bold py-1 self-center">Model Monitoring</div>
          </div>
          <div class="flex justify-end pr-8">
            <Dropdown 
            items={timeWindows}
            header={timeWindow}
            on:change={handleTimeWindowChange}
            />
          </div>
        </div> 

        <!-- Profile header -->
        <div class="flex flex-row items-center">
          <div class="m-1 text-darkpurple font-bold">Drift Configuration:</div>
            <div class="flex flex-row flex-nowrap overflow-auto p-1 items-center">
              {#if showConfig}
                <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-primary-400 hover:variant-soft-primary" on:click={toggleProfile}>
                  <div class="text-white text-xs font-bold hover:text-darkpurple">Hide</div>
                </button>
              {:else}
                <button type="button" class="m-1 border border-darkpurple btn btn-sm bg-surface-100 hover:variant-soft-primary" on:click={toggleProfile}>
                  <div class="text-darkpurple text-xs font-bold">Show</div>
                </button>
              {/if}
            </div>
        </div>

        <!-- Feature header -->
        <div class="flex flex-row items-center overflow-auto">
          <div class="m-1 text-darkpurple font-bold">Features:</div>
          <div class="py-1">
            <input
              class="input autocomplete text-sm h-7 bg-white w-full max-w-sm"
              type="search"
              name="autocomplete-search"
              bind:value={selected}
              placeholder={targetFeature}
              use:popup={popupSettings}
              />
            <div data-popup="popupAutocomplete" class="card w-48 focus:outline-primary-500 bg-white overflow-y-auto overflow-x-auto max-h-48 border border-gray-200/70 text-sm text-primary-500" tabindex="-1">
              <Autocomplete
                bind:input={selected}
                on:selection={updateFeatureValues}
                options={flavorOptions}
              />
            </div>
          </div>
        </div>

        <slot></slot>

        {#if routeViz}
        <Observability 
          routeViz={routeViz} 
          repository={repository}
          name={name}
          version={version}
          timeWindow={timeWindow}
          max_data_points={max_data_points}
          />
        {/if}

      </div>  

      {#if showConfig}
        {#if profileType === ProfileType.SPC}
          <SpcProfile 
            showConfig={showConfig} 
            repository={driftProfiles[profileType].config.repository}
            name={driftProfiles[profileType].config.name}
            version={driftProfiles[profileType].config.version}
            driftConfig={driftProfiles[profileType].config}
            driftProfile={driftProfiles[profileType]}
            on:update={handleUpdate}
            on:hide={handleHide}
            />
        {/if}
      {/if}

    {:else}
      <div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-white" id="notLoaded">
        <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

          <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">

            <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
            <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>

            <div class="mb-8 grid grid-cols-1 gap-3">
              <h2 class="text-primary-500 font-bold">No Drift Profile Detected</h2>
              <p class="mb-1 text-primary-500 text-center">
                A drift profile was not detected for this model
                If you'd like to enable monitoring, create a drift profile for this model.
              </p>

            </div>
            
          </div>
        </section>
      </div>
    {/if}
  </div>
</main>