<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedSpace: string | undefined = data.selectedSpace;
  let selectedName: string | undefined = data.selectedName;

</script>

<div class="mx-auto w-9/12 pt-20 pb-10 m500:pt-14 lg:pt-[100px] flex justify-center px-4">
  <CardsSearch 
    selectedSpace={selectedSpace}
    selectedName={selectedName}
    page={page}
  />
</div>