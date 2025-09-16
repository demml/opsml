<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedSpace: string | undefined = data.selectedSpace;
  let selectedName: string | undefined = data.selectedName;

</script>

<div class="flex-1 mx-auto w-11/12 pt-20 justify-center px-4 pb-10">
  <CardsSearch 
    selectedSpace={selectedSpace}
    selectedName={selectedName}
    page={page}
    title={data.registryType}
  />
</div>