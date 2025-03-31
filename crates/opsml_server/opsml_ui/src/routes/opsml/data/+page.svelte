<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedSpace: string | null = data.selectedSpace;

</script>

<CardsSearch 
  selectedSpace={selectedSpace}
  page={page}
/>