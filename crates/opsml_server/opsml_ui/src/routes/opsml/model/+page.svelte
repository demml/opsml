<script lang="ts">

  import type { PageProps } from './$types';
  import type { RegistryPageReturn } from '$lib/components/card/types';
  import CardSearch from '$lib/components/card/CardSearch.svelte';

  let { page, selectedName, selectedSpace, fetch }: PageProps = $props();
  
</script>

<CardSearch 
  {page} 
  {selectedName} 
  {selectedSpace} 
  {fetch}
/>



