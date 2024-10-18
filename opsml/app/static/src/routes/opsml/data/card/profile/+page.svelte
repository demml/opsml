
<script lang="ts">
  import type { DataProfile } from "$lib/scripts/data/types";
  import DataProfileDiv from "$lib/card/data/DataProfile.svelte";
  import { Autocomplete, popup  } from '@skeletonlabs/skeleton';
  import type { AutocompleteOption, PopupSettings } from '@skeletonlabs/skeleton';
  import { onMount } from 'svelte';

  /** @type {import('./$types').PageData} */
  export let data;

  let profile: DataProfile;
  $: profile = data.profile;

  let featureNames: string[];
  featureNames = data.featureNames;

  type FlavorOption = AutocompleteOption<string, { healthy: boolean }>;

  function getFlavorOptions(): FlavorOption[] {
    return featureNames.map((featureName) => {
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

  let selected: string = '';

  function onSearchSelect(event: CustomEvent<FlavorOption>): void {
		selected = event.detail.label;
    const element = document.getElementById(selected);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
	}
}

  

</script>


<div class="flex min-h-screen overflow-x-scroll bg-white">

    <div class="flex flex-col pt-4 w-full px-12 md:px-48 mb-10">

      <div class="grid grid-cols-1 md:grid-cols-2">
        <div class="text-primary-500 text-xl font-bold py-1">Data Profile</div>
        <div class="py-1">
          <input
            class="input autocomplete text-sm h-7 bg-white w-full max-w-sm"
            type="search"
            name="autocomplete-search"
            bind:value={selected}
            placeholder="Feature"
            use:popup={popupSettings}
            />
          <div data-popup="popupAutocomplete" class="card w-48 focus:outline-primary-500 bg-white overflow-y-auto overflow-x-auto max-h-48 border border-gray-200/70 text-sm text-primary-500" tabindex="-1">
            <Autocomplete
              bind:input={selected}
              on:selection={onSearchSelect}
              options={flavorOptions}
            />
          </div>
        </div>
      </div>

      <DataProfileDiv 
        profile={profile}
        featureNames = {featureNames}
      />

    </div>
</div>