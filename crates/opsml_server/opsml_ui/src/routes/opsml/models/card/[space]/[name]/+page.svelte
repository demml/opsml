<script lang="ts">

  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from "$lib/components/card/types";
  import CardSearch from '$lib/components/card/CardSearch.svelte';

  let { data }: PageProps = $props();
  let page:  RegistryPageReturn  = data.page;
  let selectedName: string | undefined = data.selectedName;
  let selectedSpace: string | undefined = data.selectedSpace;
  

</script>

<CardSearch 
  {page} 
  {selectedName} 
  {selectedSpace} 
/>



