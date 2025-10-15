<script lang="ts">

  import type { PageProps } from './$types';
  import CardSearch from '$lib/components/card/CardSearch.svelte';

  let { data }: PageProps = $props();

  console.log(JSON.stringify(data));

</script>

<CardSearch 
  page={data.page}
  selectedName={data.selectedName} 
  selectedSpace={data.selectedSpace}
/>



