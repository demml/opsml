<script lang="ts">
  import type { PageProps } from './$types';
  import CardSearch from '$lib/components/card/CardSearch.svelte';
  import { RegistryType } from '$lib/utils';
  import AgentPage from '$lib/components/card/agent/AgentPage.svelte';
  let { data }: PageProps = $props();
</script>

{#if data.registryType === RegistryType.Agent}
  <AgentPage/>
{:else}
  <CardSearch 
    page={data.page}
    selectedName={data.selectedName} 
    selectedSpace={data.selectedSpace}
  />
{/if}



