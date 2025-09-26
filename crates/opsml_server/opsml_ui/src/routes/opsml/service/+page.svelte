<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import { Switch } from '@skeletonlabs/skeleton-svelte';
  import CardTableView from "$lib/components/card/CardTableView.svelte";

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedSpace: string | undefined = data.selectedSpace;
  let selectedName: string | undefined = data.selectedName;

  let viewMode: string = $state('table');
  let viewState = $state(true);

  function toggleView() {
    viewMode = viewMode === 'table' ? 'grid' : 'table';
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
  {#if viewState}
    <div class="mb-4 text-sm text-gray-600 italic">* Table view is currently in beta. Please report any issues.</div>
    <CardTableView
      selectedSpace={selectedSpace}
      selectedName={selectedName}
      page={page}
      title={data.registryType}
      />
  {:else}
      <CardsSearch
      selectedSpace={selectedSpace}
      selectedName={selectedName}
      page={page}
      title={data.registryType}
    />
  {/if}


</div>